# Operations and Deployment Plan

## Hosting Environment Selection
- **Environment**: Managed VPS provider (e.g., DigitalOcean, Linode) to balance operational control with simplified hardware management.
- **Rationale**:
  - Predictable monthly costs without purchasing physical hardware.
  - Provider handles underlying hardware redundancy, networking, and physical security.
  - Rapid scaling via snapshots or larger VPS sizes.
  - API support for automation and integration with CI/CD pipeline.
- **Capacity Planning**:
  - Start with 4 vCPU / 8 GB RAM / 160 GB SSD VPS for application and worker services.
  - Separate managed PostgreSQL service tier with automated failover and backups.
  - Use block storage volume (200 GB) for static/media assets to allow independent scaling.

## Infrastructure Components
| Component | Selection | Notes |
| --- | --- | --- |
| Operating System | Ubuntu Server 22.04 LTS | Long-term support, strong community, available on most VPS providers. |
| Application Runtime | Python 3.11, Django app served via Gunicorn (4 workers, 2 threads) | Gunicorn behind Nginx reverse proxy; worker count tuned per CPU and memory profiling. |
| Web Server / Reverse Proxy | Nginx 1.24 | Handles TLS termination, static file serving, request buffering, and load balancing to Gunicorn/worker pods. |
| Process Supervisor | systemd service units | Manage Gunicorn, Celery workers, scheduled tasks; enables automatic restarts. |
| Static Assets | Collected to `/var/www/app/static/` and served via Nginx | Use `collectstatic` during deployment, sync to block storage volume. |
| Media Storage | Object storage bucket (e.g., DigitalOcean Spaces or S3-compatible) | Access via signed URLs; Django `storages` configured with env credentials. |
| Background Tasks | Celery + Redis | Redis managed service (TLS-enabled) for message broker and caching. |
| TLS Certificates | Managed via Let's Encrypt + certbot | Automated renewal cron/systemd timer every 12 hours. |

## Deployment Pipeline

### Git Workflow
- Adopt trunk-based development with short-lived feature branches.
- Branch naming: `feature/<description>` or `hotfix/<issue>`.
- Pull requests require code review, automated tests, and status checks before merging into `main`.
- Use conventional commits for traceable history.

### CI/CD Steps
1. **CI (GitHub Actions)**
   - Trigger on pull request and push to `main`.
   - Jobs: linting (flake8, black --check), unit tests (pytest), integration tests (Django tests), security scan (bandit, pip-audit).
   - Cache dependencies via pip cache.
2. **Build Artifact**
   - On successful `main` build, create Docker image tagged `app:<git-sha>`.
   - Push image to container registry (e.g., GHCR or Docker Hub) with SBOM metadata.
3. **CD (GitHub Actions Workflow)**
   - Trigger manual `Deploy` workflow or automatically on tagged release.
   - Steps:
     1. Fetch latest secrets from secret manager (e.g., Doppler or AWS Secrets Manager).
     2. Connect to VPS via SSH using deploy key.
     3. Pull new Docker image.
     4. Run database migrations (`python manage.py migrate`) with maintenance page enabled.
     5. Run `collectstatic` and sync static assets.
     6. Reload Gunicorn/Nginx via systemd.
     7. Run smoke tests (health check endpoint, key API).
   - Notifications to Slack/MS Teams on success/failure.

### Environment Variables Management
- Store secrets in managed secrets vault (e.g., 1Password Secrets Automation or HashiCorp Vault). No secrets committed to repo.
- CI accesses secrets via OIDC trust; production host pulls runtime secrets via `envdir` files maintained by configuration management (Ansible).
- Maintain `.env.example` for non-secret defaults; production `.env` stored encrypted (age/sops).

### Rollback Procedures
1. **Application Rollback**
   - Maintain previous Docker image tags (`app:<previous-sha>`).
   - Systemd service file uses symlink `/opt/app/current` pointing to release directory.
   - Rollback steps:
     1. `sudo systemctl stop app.service`
     2. Update symlink to previous release (`ln -sfn /opt/app/releases/<prev> /opt/app/current`).
     3. `sudo systemctl start app.service`
     4. Verify health checks.
2. **Database Rollback**
   - Prefer forward-only migrations; rollback via restore from latest backup if critical (requires downtime).
   - Maintain migration playbooks; test `manage.py migrate <app> <migration>` in staging before production.
3. **Configuration Rollback**
   - Track system configuration in Git (Ansible playbooks). Rollback by reapplying last-known-good tag.

## PostgreSQL Backup Strategy
- **Service**: Managed PostgreSQL with point-in-time recovery (PITR).
- **Schedule**:
  - Incremental WAL archiving continuous.
  - Nightly full backup at 02:00 UTC.
- **Retention**:
  - PITR logs retained for 14 days.
  - Weekly snapshot retained for 3 months.
  - Monthly snapshot retained for 1 year for compliance.
- **Validation**:
  - Quarterly restore drills to staging environment to verify backup integrity.
  - Automated backup completion alerts.

## Monitoring and Logging
- **Infrastructure Monitoring**: Use Prometheus + Grafana managed service for VPS metrics (CPU, RAM, disk, network) and custom app metrics via `/metrics` endpoint.
- **Application Performance Monitoring**: Sentry for error tracking; OpenTelemetry exports to Grafana Tempo/Logs.
- **Log Aggregation**: Filebeat/Fluent Bit ship logs to ELK stack (ElasticSearch, Kibana) or hosted alternative (Logtail, LogDNA).
- **Alerting**: Configure alert rules for high error rates, high latency, CPU/memory saturation, disk usage, failed backups, certificate expiry.
- **Availability Checks**: UptimeRobot or StatusCake synthetic monitoring hitting health and key user flows.

## Routine Maintenance
- **Database Migrations**: Run via CI/CD pipeline with maintenance window toggle; include pre- and post-migration checks.
- **Package Updates**:
  - Weekly dependabot PRs; apply security patches within 48 hours.
  - Monthly OS package updates using unattended-upgrades with manual reboot plan.
- **Security Audits**: Quarterly vulnerability scan (Lynis, OpenVAS) and review firewall rules.
- **Capacity Review**: Monthly review of resource usage and adjust VPS size/storage as needed.

## Admin Access Management
- **Onboarding**:
  - Create ticket referencing approval.
  - Provision SSO account and assign role in IAM/IdP.
  - Add to password manager vault and GitHub organization with least privilege.
  - Grant SSH access via adding public key to Ansible-managed `deployers` group.
  - Provide training on runbooks and incident response.
- **Offboarding**:
  - Disable SSO account immediately.
  - Remove from GitHub, monitoring tools, secrets manager.
  - Revoke SSH keys and rotate shared secrets (DB passwords, API keys) if necessary.
  - Document completion in access log.

## Security Practices
- **SSL/TLS**: Enforce HTTPS with HSTS (max-age 6 months, includeSubDomains, preload). Use TLS 1.2+ with strong cipher suites.
- **Firewall Rules**:
  - Allow inbound ports: 22 (SSH, restricted to office VPN/IPs), 80/443 (HTTP/HTTPS). Block all others.
  - Outbound allow list for package repos, database, object storage, monitoring endpoints.
  - Use cloud firewalls + host-based UFW with matching rules.
- **Network Segmentation**: Place database and Redis in private network inaccessible from internet.
- **Secrets Handling**: Rotate secrets quarterly or upon personnel change. Use `sudo` with logging.
- **Compliance**: Maintain audit log retention 1 year, follow GDPR data handling policies.

## Documentation and Operational Playbooks
- Maintain version-controlled runbooks in `docs/ops/` (see structure below).
- Required documents:
  - Deployment Runbook
  - Incident Response Playbook (SEV-1/2/3 definitions, escalation tree)
  - Backup Restore Procedure
  - Monitoring & Alert Tuning Guide
  - Access Management SOP
  - Change Management Policy

## Production Readiness Checklist
1. **Architecture & Infrastructure**
   - [ ] VPS provisioned with base image, hardening applied (CIS baseline, fail2ban).
   - [ ] Nginx/Gunicorn configuration validated with staging load test.
   - [ ] TLS certificates installed and auto-renew tested.
   - [ ] Static/media storage configured with lifecycle policies.
2. **Application**
   - [ ] All migrations applied successfully in staging.
   - [ ] Smoke and regression test suites passing.
   - [ ] Feature flags configured for staged rollouts.
   - [ ] Logging levels verified (no sensitive data in logs).
3. **Data & Backups**
   - [ ] PITR backups enabled and restore drill completed in last 90 days.
   - [ ] Database credentials stored in vault; rotation schedule documented.
   - [ ] Data retention policies implemented (GDPR compliance).
4. **Security**
   - [ ] Firewall rules enforced; ports scanned (nmap) for verification.
   - [ ] Vulnerability scan with no unresolved critical findings.
   - [ ] Admin onboarding/offboarding process tested.
   - [ ] WAF/rate limiting configured for API endpoints.
5. **Monitoring & Alerting**
   - [ ] Dashboards cover key KPIs (latency, error rate, throughput).
   - [ ] Alerts defined with on-call rotation and escalation policy.
   - [ ] Synthetic monitoring active with notifications validated.
6. **Operations**
   - [ ] Deployment and rollback runbooks reviewed and accessible.
   - [ ] On-call schedule published; contact info validated.
   - [ ] Support tools (status page, incident channel) ready.
   - [ ] Business continuity plan validated with stakeholders.

## Pre-Go-Live Runbook (High-Level)
1. **T-7 Days**
   - Finalize release candidate; freeze non-critical changes.
   - Complete security and compliance checks.
   - Confirm backups and restore drill results.
2. **T-3 Days**
   - Execute load test on staging with production parity.
   - Review monitoring dashboards and alert thresholds.
   - Conduct go/no-go meeting with stakeholders.
3. **T-1 Day**
   - Tag release and generate deployment package.
   - Ensure all secrets updated and deployed to target.
   - Notify support and end users of deployment window.
4. **Deployment Window**
   - Follow deployment pipeline steps; maintain real-time log of actions.
   - Run smoke tests immediately post-deploy.
   - Monitor metrics for 1 hour; keep rollback plan ready.
5. **Post-Deployment**
   - Announce success/failure; update status page.
   - Create post-deployment report with metrics and incidents.
   - Schedule retrospective to capture lessons learned.

## Future Enhancements
- Evaluate infrastructure-as-code (Terraform) for full environment provisioning.
- Implement blue-green deployments once traffic warrants continuous uptime.
- Consider managed WAF and DDoS protection services for higher security posture.

