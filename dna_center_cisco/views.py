from django.shortcuts import render
from django.http import HttpRequest
from .dnac_api import dnac_manager, log_action


def _ensure_token(request: HttpRequest):
    """
    Helper: garante que temos um token.
    - Se já existir na sessão, reaproveita.
    - Senão, chama get_auth_token e salva.
    Retorna (success, error_message).
    """
    token_in_session = request.session.get("dnac_token")
    if token_in_session:
        dnac_manager.token = token_in_session
        return True, None

    success, err = dnac_manager.get_auth_token()
    if success:
        request.session["dnac_token"] = dnac_manager.token
        return True, None
    else:
        return False, err or "Authentication failed."


def home_view(request):
    """Simple home with links to the three main features."""
    return render(request, "dna_center_cisco/home.html")


def authenticate_view(request):
    """
    View 1: Authenticate & Show Token
    """
    success, err = dnac_manager.get_auth_token()
    context = {}

    if success:
        request.session["dnac_token"] = dnac_manager.token
        log_action(action="authenticate", status="success")
        context["token"] = dnac_manager.token
    else:
        log_action(action="authenticate", status="failure", message=err)
        context["token"] = None
        context["error"] = err

    return render(request, "dna_center_cisco/auth.html", context)


def devices_view(request):
    """
    View 2: List Network Devices
    """
    ok, err = _ensure_token(request)
    context = {}

    if not ok:
        log_action(action="list_devices", status="failure", message=err)
        context["error"] = f"Authentication error: {err}"
        context["devices"] = []
        return render(request, "dna_center_cisco/devices.html", context)

    devices, err = dnac_manager.get_network_devices()
    if devices is not None:
        log_action(action="list_devices", status="success")
        context["devices"] = devices
        context["error"] = None
    else:
        log_action(action="list_devices", status="failure", message=err)
        context["devices"] = []
        context["error"] = err or "Could not retrieve devices."

    return render(request, "dna_center_cisco/devices.html", context)


def interfaces_view(request):
    """
    View 3: Show Device Interfaces by IP
    """
    device_ip = ""
    interfaces = []
    error = None

    if request.method == "POST":
        device_ip = request.POST.get("device_ip", "").strip()

        ok, err = _ensure_token(request)
        if not ok:
            log_action(
                action="show_interfaces",
                status="failure",
                device_ip=device_ip,
                message=err
            )
            error = f"Authentication error: {err}"
        else:
            interfaces, err = dnac_manager.get_device_interfaces(device_ip)
            if interfaces is not None:
                log_action(
                    action="show_interfaces",
                    status="success",
                    device_ip=device_ip
                )
            else:
                log_action(
                    action="show_interfaces",
                    status="failure",
                    device_ip=device_ip,
                    message=err
                )
                error = err or "Could not retrieve interfaces."
                interfaces = []

    context = {
        "device_ip": device_ip,
        "interfaces": interfaces,
        "error": error,
    }
    return render(request, "dna_center_cisco/interfaces.html", context)
