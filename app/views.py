from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Count, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, FormView, ListView, TemplateView

from .forms import LoginForm, PassFilterForm, PassForm, SecurityVerificationForm, SignUpForm
from .mixins import RoleRequiredMixin
from .models import Log, Pass, User


class HomeRedirectView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("dashboard")
        return redirect("login")


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("dashboard")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, "Your account has been created successfully.")
        return response


class CustomLoginView(LoginView):
    authentication_form = LoginForm
    template_name = "registration/login.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, "Welcome back.")
        return super().form_valid(form)


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("login")


class DashboardRedirectView(RoleRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.role == User.Roles.ADMIN:
            return redirect("admin-dashboard")
        if request.user.role == User.Roles.SECURITY:
            return redirect("security-dashboard")
        return redirect("user-dashboard")


class UserDashboardView(RoleRequiredMixin, ListView):
    allowed_roles = (User.Roles.USER,)
    model = Pass
    template_name = "dashboard/user_dashboard.html"
    context_object_name = "passes"
    paginate_by = 5

    def get_queryset(self):
        queryset = Pass.objects.filter(user=self.request.user)
        self.filter_form = PassFilterForm(self.request.GET or None)
        if self.filter_form.is_valid():
            search = self.filter_form.cleaned_data.get("search")
            date = self.filter_form.cleaned_data.get("date")
            status = self.filter_form.cleaned_data.get("status")
            if search:
                queryset = queryset.filter(pass_id__icontains=search)
            if date:
                queryset = queryset.filter(out_time__date=date)
            if status:
                queryset = queryset.filter(status=status)
        return queryset.select_related("user")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_passes = Pass.objects.filter(user=self.request.user)
        context["filter_form"] = self.filter_form
        context["total_passes"] = user_passes.count()
        context["approved_count"] = user_passes.filter(status=Pass.Status.APPROVED).count()
        context["pending_count"] = user_passes.filter(status=Pass.Status.PENDING).count()
        context["rejected_count"] = user_passes.filter(status=Pass.Status.REJECTED).count()
        return context


class ApplyPassView(RoleRequiredMixin, CreateView):
    allowed_roles = (User.Roles.USER,)
    form_class = PassForm
    template_name = "passes/apply_pass.html"
    success_url = reverse_lazy("user-dashboard")

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Pass request submitted successfully.")
        return super().form_valid(form)


class PassListView(RoleRequiredMixin, ListView):
    allowed_roles = (User.Roles.USER,)
    model = Pass
    template_name = "passes/pass_list.html"
    context_object_name = "passes"
    paginate_by = 10

    def get_queryset(self):
        queryset = Pass.objects.filter(user=self.request.user).select_related("user")
        self.filter_form = PassFilterForm(self.request.GET or None)
        if self.filter_form.is_valid():
            search = self.filter_form.cleaned_data.get("search")
            date = self.filter_form.cleaned_data.get("date")
            status = self.filter_form.cleaned_data.get("status")
            if search:
                queryset = queryset.filter(pass_id__icontains=search)
            if date:
                queryset = queryset.filter(out_time__date=date)
            if status:
                queryset = queryset.filter(status=status)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter_form"] = self.filter_form
        return context


class AdminDashboardView(RoleRequiredMixin, ListView):
    allowed_roles = (User.Roles.ADMIN,)
    model = Pass
    template_name = "dashboard/admin_dashboard.html"
    context_object_name = "passes"
    paginate_by = 10

    def get_queryset(self):
        queryset = Pass.objects.select_related("user")
        self.filter_form = PassFilterForm(self.request.GET or None)
        if self.filter_form.is_valid():
            search = self.filter_form.cleaned_data.get("search")
            date = self.filter_form.cleaned_data.get("date")
            status = self.filter_form.cleaned_data.get("status")
            if search:
                queryset = queryset.filter(
                    Q(pass_id__icontains=search)
                    | Q(user__username__icontains=search)
                    | Q(department__icontains=search)
                )
            if date:
                queryset = queryset.filter(out_time__date=date)
            if status:
                queryset = queryset.filter(status=status)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        counts = Pass.objects.aggregate(
            total_passes=Count("id"),
            approved_count=Count("id", filter=Q(status=Pass.Status.APPROVED)),
            pending_count=Count("id", filter=Q(status=Pass.Status.PENDING)),
            rejected_count=Count("id", filter=Q(status=Pass.Status.REJECTED)),
        )
        context.update(counts)
        context["filter_form"] = self.filter_form
        context["logs"] = Log.objects.select_related("gate_pass", "gate_pass__user")[:8]
        return context


class PassStatusUpdateView(RoleRequiredMixin, View):
    allowed_roles = (User.Roles.ADMIN,)

    def post(self, request, *args, **kwargs):
        gate_pass = get_object_or_404(Pass, pk=kwargs["pk"])
        new_status = request.POST.get("status")
        if new_status not in {Pass.Status.APPROVED, Pass.Status.REJECTED}:
            raise Http404("Invalid status")
        gate_pass.status = new_status
        gate_pass.save(update_fields=["status", "updated_at"])
        messages.success(request, f"{gate_pass.pass_id} marked as {new_status}.")
        return redirect("admin-dashboard")


class SecurityDashboardView(RoleRequiredMixin, FormView):
    allowed_roles = (User.Roles.SECURITY,)
    form_class = SecurityVerificationForm
    template_name = "dashboard/security_dashboard.html"
    success_url = reverse_lazy("security-dashboard")

    def form_valid(self, form):
        pass_id = form.cleaned_data["pass_id"].upper()
        gate_pass = (
            Pass.objects.select_related("user")
            .prefetch_related("logs")
            .filter(pass_id=pass_id)
            .first()
        )
        if gate_pass:
            return self.render_to_response(self.get_context_data(form=form, pass_record=gate_pass))
        messages.error(self.request, "Pass ID not found.")
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recent_logs"] = Log.objects.select_related("gate_pass", "gate_pass__user")[:10]
        return context


class LogActionView(RoleRequiredMixin, View):
    allowed_roles = (User.Roles.SECURITY,)

    def post(self, request, *args, **kwargs):
        gate_pass = get_object_or_404(Pass, pass_id=kwargs["pass_id"])
        action = request.POST.get("action")

        if gate_pass.status != Pass.Status.APPROVED:
            messages.error(request, "Only approved passes can be marked at the gate.")
            return redirect("security-dashboard")

        latest_log = gate_pass.logs.first()
        now = timezone.now()

        if action == "entry":
            if latest_log and latest_log.entry_time and not latest_log.exit_time:
                messages.info(request, "Entry is already marked for this pass.")
            else:
                Log.objects.create(gate_pass=gate_pass, entry_time=now)
                messages.success(request, f"Entry marked for {gate_pass.pass_id}.")
        elif action == "exit":
            if latest_log and latest_log.entry_time and not latest_log.exit_time:
                latest_log.exit_time = now
                latest_log.save(update_fields=["exit_time"])
                messages.success(request, f"Exit marked for {gate_pass.pass_id}.")
            else:
                messages.error(request, "Entry must be marked before exit.")
        else:
            raise Http404("Invalid action")
        return redirect("security-dashboard")
