# Network Security Automation Repository Plan 
The repository plan will be a public, production-grade repo that shows network security automation for security operations dealing with end-to-end (discovery -> change -> audit -> rollback), with tight controls (dry-run , approvals, secrets handling, logging, and tests).

## Time to start Early 2026
### Files Needed in the Repository:
* Docs
  * architecture
  * threat-model
  * credential-handling
  * runbooks
    * onboarding
    * adding a new integration

* Integrations
  * PanOS
    * global-protect portal/passcode rotation (where allowed)
    * address object / group reconciliation
    * rule shadowing / unused rule detection (with suggested cleanup)
  * Cisco 
  * Qualys
  * fortinet
  * tenable
  * servicenow

* Playbooks 
  * egress_ip_verify
  * globalprotect_passcode_rotate
  * firewall_rule_hygiene
  * vuln_ticket_Dedupe

