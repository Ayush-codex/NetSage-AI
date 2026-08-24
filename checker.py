import re
import ipaddress
from typing import Optional




def check_interface_status(show_output: str) -> list:
    

    errors = []

    
    patterns = [
        re.compile(
            r"(?P<interface>"
            r"(?:GigabitEthernet|FastEthernet|Ethernet|Serial|"
            r"TenGigabitEthernet|Loopback|Vlan)"
            r"[\w./-]*"
            r")\s+is\s+"
            r"(?P<status>administratively down|down|up)"
            r",?\s*"
            r"(?:line protocol is\s+"
            r"(?P<protocol>down|up))?",
            re.IGNORECASE
        ),

        re.compile(
            r"(?P<interface>"
            r"(?:Gi|Fa|Eth|Se|Te|Lo|Vl)"
            r"[\w./-]*"
            r")\s+is\s+"
            r"(?P<status>administratively down|down|up)"
            r",?\s*"
            r"(?:line protocol is\s+"
            r"(?P<protocol>down|up))?",
            re.IGNORECASE
        )
    ]

    detected_interfaces = set()

    for pattern in patterns:

        for match in pattern.finditer(show_output):

            interface = match.group(
                "interface"
            )

            status = match.group(
                "status"
            ).lower()

            protocol = match.group(
                "protocol"
            )

            if protocol:
                protocol = protocol.lower()

            
            if interface in detected_interfaces:
                continue

            
            if status == "administratively down":

                errors.append({
                    "type": "INTERFACE_ADMINISTRATIVELY_DOWN",
                    "severity": "High",
                    "interface": interface,
                    "status": status,
                    "line_protocol": protocol,
                    "evidence": match.group(0).strip(),
                    "message": (
                        f"{interface} is "
                        "administratively down."
                    )
                })

                detected_interfaces.add(interface)

            

            elif status == "down" or protocol == "down":

                errors.append({
                    "type": "INTERFACE_DOWN",
                    "severity": "High",
                    "interface": interface,
                    "status": status,
                    "line_protocol": protocol,
                    "evidence": match.group(0).strip(),
                    "message": (
                        f"{interface} has a down "
                        "status or line protocol."
                    )
                })

                detected_interfaces.add(interface)

    return errors




def check_vlan_exists(
    show_output: str,
    required_vlan: Optional[str] = None
) -> list:

    errors = []

    if not required_vlan:
        return errors

    pattern = re.compile(
        rf"^\s*{re.escape(required_vlan)}\s+\S+",
        re.MULTILINE
    )

    if not pattern.search(show_output):

        errors.append({
            "type": "VLAN_MISSING",
            "severity": "High",
            "vlan": required_vlan,
            "evidence": (
                f"VLAN {required_vlan} was not found "
                "in the provided output."
            ),
            "message": (
                f"Required VLAN {required_vlan} "
                "appears to be missing."
            )
        })

    return errors




def check_route_exists(
    show_output: str,
    required_network: Optional[str] = None
) -> list:

    errors = []

    if not required_network:
        return errors

    if required_network not in show_output:

        errors.append({
            "type": "ROUTE_MISSING",
            "severity": "High",
            "network": required_network,
            "evidence": (
                f"{required_network} was not found "
                "in the routing table."
            ),
            "message": (
                f"No route for {required_network} "
                "was detected."
            )
        })

    return errors




def check_gateway_subnet(
    ip_address: Optional[str] = None,
    subnet_mask: Optional[str] = None,
    gateway: Optional[str] = None
) -> list:

    errors = []

    if not ip_address or not subnet_mask or not gateway:
        return errors

    try:

        network = ipaddress.IPv4Network(
            f"{ip_address}/{subnet_mask}",
            strict=False
        )

        gateway_ip = ipaddress.IPv4Address(gateway)

        if gateway_ip not in network:

            errors.append({
                "type": "GATEWAY_MISMATCH",
                "severity": "High",
                "ip_address": ip_address,
                "subnet_mask": subnet_mask,
                "gateway": gateway,
                "evidence": (
                    f"Host subnet: {network}; "
                    f"Gateway: {gateway}"
                ),
                "message": (
                    "Default gateway is outside "
                    "the host subnet."
                )
            })

    except ValueError as error:

        errors.append({
            "type": "INVALID_IP_CONFIGURATION",
            "severity": "High",
            "evidence": str(error),
            "message": "Invalid IP configuration."
        })

    return errors




def check_duplicate_ips(
    ip_addresses: Optional[list] = None
) -> list:

    errors = []

    if not ip_addresses:
        return errors

    seen = set()

    for ip in ip_addresses:

        if ip in seen:

            errors.append({
                "type": "DUPLICATE_IP",
                "severity": "High",
                "ip_address": ip,
                "evidence": (
                    f"IP address {ip} appears more than once."
                ),
                "message": (
                    f"Duplicate IP address detected: {ip}"
                )
            })

        seen.add(ip)

    return errors




def check_vlan_mismatch(
    configured_vlan: Optional[str] = None,
    expected_vlan: Optional[str] = None
) -> list:

    errors = []

    if not configured_vlan or not expected_vlan:
        return errors

    if str(configured_vlan) != str(expected_vlan):

        errors.append({
            "type": "VLAN_MISMATCH",
            "severity": "High",
            "configured_vlan": configured_vlan,
            "expected_vlan": expected_vlan,
            "evidence": (
                f"Configured VLAN: {configured_vlan}; "
                f"Expected VLAN: {expected_vlan}"
            ),
            "message": (
                "Interface VLAN assignment does not "
                "match the expected VLAN."
            )
        })

    return errors




def check_dhcp(
    show_output: str,
    expected_gateway: Optional[str] = None
) -> list:

    errors = []

    output_lower = show_output.lower()

    if "no address" in output_lower:

        errors.append({
            "type": "DHCP_NO_ADDRESS",
            "severity": "High",
            "evidence": show_output.strip(),
            "message": (
                "DHCP appears unable to provide "
                "an address."
            )
        })

    if "pool" in output_lower and "exhausted" in output_lower:

        errors.append({
            "type": "DHCP_POOL_EXHAUSTED",
            "severity": "High",
            "evidence": show_output.strip(),
            "message": "DHCP address pool may be exhausted."
        })

    if expected_gateway and expected_gateway not in show_output:

        if "default-router" in output_lower:

            errors.append({
                "type": "DHCP_GATEWAY_MISMATCH",
                "severity": "Medium",
                "evidence": show_output.strip(),
                "message": (
                    "Expected DHCP gateway was not "
                    "found in the provided output."
                )
            })

    return errors




def check_acl(show_output: str) -> list:

    errors = []

    output_lower = show_output.lower()

    if "deny" in output_lower:

        errors.append({
            "type": "ACL_DENY_PRESENT",
            "severity": "High",
            "evidence": show_output.strip(),
            "message": (
                "ACL output contains a deny rule. "
                "Further verification is required."
            )
        })

    return errors




def check_nat(show_output: str) -> list:

    errors = []

    output_lower = show_output.lower()

    if (
        "overload" not in output_lower
        and "ip nat inside source" in output_lower
    ):

        errors.append({
            "type": "NAT_OVERLOAD_MISSING",
            "severity": "Medium",
            "evidence": show_output.strip(),
            "message": (
                "NAT configuration exists but "
                "overload was not detected."
            )
        })

    if "no translations" in output_lower:

        errors.append({
            "type": "NAT_NO_TRANSLATIONS",
            "severity": "High",
            "evidence": show_output.strip(),
            "message": (
                "No NAT translations were detected."
            )
        })

    return errors



def check_ospf(show_output: str) -> list:

    errors = []

    hello_values = re.findall(
        r"hello[- ]interval\s+(\d+)",
        show_output,
        re.IGNORECASE
    )

    if len(hello_values) >= 2:

        if len(set(hello_values)) > 1:

            errors.append({
                "type": "OSPF_HELLO_MISMATCH",
                "severity": "High",
                "evidence": (
                    f"Detected hello intervals: "
                    f"{', '.join(hello_values)}"
                ),
                "message": (
                    "OSPF hello intervals do not match."
                )
            })

    if "neighbor" in show_output.lower():

        if (
            "down" in show_output.lower()
            or "dead" in show_output.lower()
        ):

            errors.append({
                "type": "OSPF_NEIGHBOR_PROBLEM",
                "severity": "High",
                "evidence": show_output.strip(),
                "message": (
                    "OSPF neighbor status may indicate "
                    "an adjacency problem."
                )
            })

    return errors



def get_relevant_rules(concept_tag: str) -> list:
    """
    Determine which deterministic checks are relevant
    for a troubleshooting case.
    """

    concept = concept_tag.lower()

    rules = []

    if any(
        keyword in concept
        for keyword in [
            "interface",
            "switching",
            "inter-vlan",
            "routing",
            "vlan"
        ]
    ):
        rules.append("interface")

    if any(
        keyword in concept
        for keyword in [
            "vlan",
            "trunk"
        ]
    ):
        rules.append("vlan")

    if any(
        keyword in concept
        for keyword in [
            "routing",
            "inter-vlan",
            "ospf",
            "static"
        ]
    ):
        rules.append("routing")

    if any(
        keyword in concept
        for keyword in [
            "addressing",
            "gateway",
            "dhcp"
        ]
    ):
        rules.append("ip")

    if "dhcp" in concept:
        rules.append("dhcp")

    if "acl" in concept or "wireless/acl" in concept:
        rules.append("acl")

    if "nat" in concept:
        rules.append("nat")

    if "ospf" in concept:
        rules.append("ospf")

    return list(dict.fromkeys(rules))



def diagnose_case(case: dict) -> dict:
    """
    Run deterministic checks against a complete
    NetSage AI troubleshooting case.
    """

    show_output = str(
        case.get("show_outputs", "")
    )

    concept_tag = str(
        case.get("concept_tag", "")
    )

    rules = get_relevant_rules(
        concept_tag
    )

    errors = []


    if "interface" in rules:

        errors.extend(
            check_interface_status(
                show_output
            )
        )

    

    if "vlan" in rules:

        errors.extend(
            check_vlan_exists(
                show_output
            )
        )

    

    if "routing" in rules:

        errors.extend(
            check_route_exists(
                show_output
            )
        )

    

    if "ip" in rules:

        errors.extend(
            check_gateway_subnet(
                case.get("ip_address"),
                case.get("subnet_mask"),
                case.get("gateway")
            )
        )

    

    if "dhcp" in rules:

        errors.extend(
            check_dhcp(
                show_output
            )
        )

    

    if "acl" in rules:

        errors.extend(
            check_acl(
                show_output
            )
        )

    

    if "nat" in rules:

        errors.extend(
            check_nat(
                show_output
            )
        )

    

    if "ospf" in rules:

        errors.extend(
            check_ospf(
                show_output
            )
        )

    

    if errors:

        status = "ERRORS_DETECTED"

    else:

        status = "NO_KNOWN_ERRORS"

    return {
        "case_id": case.get("case_id"),
        "concept_tag": concept_tag,
        "status": status,
        "rules_checked": rules,
        "error_count": len(errors),
        "errors": errors
    }




def run_checks(
    show_output: str,
    required_vlan: Optional[str] = None,
    required_network: Optional[str] = None,
    ip_address: Optional[str] = None,
    subnet_mask: Optional[str] = None,
    gateway: Optional[str] = None,
    ip_addresses: Optional[list] = None,
    configured_vlan: Optional[str] = None,
    expected_vlan: Optional[str] = None,
    expected_dhcp_gateway: Optional[str] = None
) -> dict:

    all_errors = []

    
    all_errors.extend(
        check_interface_status(show_output)
    )

    
    all_errors.extend(
        check_vlan_exists(
            show_output,
            required_vlan
        )
    )

    
    all_errors.extend(
        check_route_exists(
            show_output,
            required_network
        )
    )

    
    all_errors.extend(
        check_gateway_subnet(
            ip_address,
            subnet_mask,
            gateway
        )
    )

    
    all_errors.extend(
        check_duplicate_ips(
            ip_addresses
        )
    )

    
    all_errors.extend(
        check_vlan_mismatch(
            configured_vlan,
            expected_vlan
        )
    )

    
    all_errors.extend(
        check_dhcp(
            show_output,
            expected_dhcp_gateway
        )
    )

    
    all_errors.extend(
        check_acl(show_output)
    )

    
    all_errors.extend(
        check_nat(show_output)
    )

    #
    all_errors.extend(
        check_ospf(show_output)
    )

    
    if all_errors:
        status = "ERRORS_DETECTED"
    else:
        status = "NO_KNOWN_ERRORS"

    return {
        "status": status,
        "error_count": len(all_errors),
        "errors": all_errors
    }
