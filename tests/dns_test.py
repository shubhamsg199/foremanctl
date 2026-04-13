import json

import pytest


FOREMAN_PROXY_PORT = 8443


@pytest.fixture(scope="module")
def dns_base_secret(server):
    return server.run(
        "podman secret inspect --showsecret --format '{{.SecretData}}' foreman-proxy-dns-yml"
    )


def test_dns_feature_registered(server, certificates, server_fqdn):
    """Verify the smart proxy reports DNS in its features list."""
    cmd = server.run(
        f"curl --cacert {certificates['ca_certificate']} "
        f"--silent https://{server_fqdn}:{FOREMAN_PROXY_PORT}/features"
    )
    assert cmd.succeeded
    features = json.loads(cmd.stdout)
    assert "dns" in features


def test_dns_base_config_secret_exists(dns_base_secret):
    """Verify the base dns.yml podman secret was created."""
    assert dns_base_secret.succeeded


def test_dns_base_config_enabled(dns_base_secret):
    """Verify DNS is enabled in the base config."""
    assert ':enabled: true' in dns_base_secret.stdout


def test_dns_base_config_provider(dns_base_secret):
    """Verify the configured provider appears in the base config."""
    assert ':use_provider: dns_' in dns_base_secret.stdout


def test_dns_base_config_ttl(dns_base_secret):
    """Verify the TTL is set in the base config."""
    assert ':dns_ttl:' in dns_base_secret.stdout


def test_foreman_proxy_running_with_dns(server):
    """Verify the smart proxy service is running after DNS is enabled."""
    foreman_proxy = server.service("foreman-proxy")
    assert foreman_proxy.is_running


def test_foreman_proxy_reachable_with_dns(server):
    """Verify the smart proxy port is reachable after DNS is enabled."""
    foreman_proxy = server.addr('localhost')
    assert foreman_proxy.port(FOREMAN_PROXY_PORT).is_reachable
