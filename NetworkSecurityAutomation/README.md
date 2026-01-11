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



## Apps
**Exposure Drift Detector** : Exposure Drift Detector using python-nmap

- Scans a CIDR/host list for a focused set of "risky" ports
- Saves current findings to JSON
- Optionally diffs vs a previous baseline and prints NEW exposures

Ethics: scan only systems you own or have explicit permission to test.

#### Run it: 
```python3 exposure_drift_poc.py --targets 192.168.1.0/24 --out baseline.json```

#### Run the diff: 
```python3 exposure_drift_poc.py --targets 192.168.1.0/24 --out current.json --baseline baseline.json```

### Exit codes:

* 0 = no new exposures (or no baseline used)

* 1 = new exposures detected

* 2 = baseline file missing