##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##
##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##
#
#  Model-0: the fine-grained original model
#
##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##
##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##-##


# BusinessActor
_BusinessActor(accounting_office)
_BusinessActor(administration_office)
_BusinessActor(customer)
_BusinessActor(customer_support_office)
_BusinessActor(executives)
_BusinessActor(human_resource_office)
_BusinessActor(production_office)
_BusinessActor(sales_contractor)

# ApplicationComponent
_ApplicationComponent(accounting)
_ApplicationComponent(asset_management)
_ApplicationComponent(communication)
_ApplicationComponent(customer_relationship_management)
_ApplicationComponent(enterprise_resource_planning)
_ApplicationComponent(human_resource_management)
_ApplicationComponent(sales_force_automation)

# DataObject
_DataObject(assets)
_DataObject(customers)
_DataObject(documents)
_DataObject(human_resources)
_DataObject(materials)
_DataObject(messages)
_DataObject(purchase_contracts)
_DataObject(sales_contracts)

# Device
_Device(communication_cloud_service)
_Device(customer_application_server)
_Device(customer_device)
_Device(database_server)
_Device(internal_application_server)
_Device(internal_web_server)
_Device(managed_laptops)
_Device(managed_mobile_phones)
_Device(public_web_server)
_Device(secured_laptops)
_Device(secured_mobile_phones)
_Device(unmanaged_laptops)
_Device(unmanaged_mobile_phones)

# Artifact
_Artifact(database)
_Artifact(document_files)
_Artifact(message_files)

# CommunicationNetwork
_CommunicationNetwork(private_lan)
_CommunicationNetwork(public_lan)
_CommunicationNetwork(the_internet)
_CommunicationNetwork(vpn)

# Device serves BusinessActor
serves(customer_device, customer)
serves(unmanaged_mobile_phones, sales_contractor)
serves(unmanaged_laptops, sales_contractor)
serves(managed_mobile_phones, accounting_office)
serves(managed_laptops, accounting_office)
serves(secured_mobile_phones, executives)
serves(secured_laptops, executives)
serves(managed_mobile_phones, production_office)
serves(managed_mobile_phones, customer_support_office)
serves(managed_mobile_phones, administration_office)
serves(managed_mobile_phones, human_resource_office)
serves(managed_laptops, administration_office)
serves(managed_laptops, human_resource_office)
serves(managed_laptops, production_office)
serves(managed_laptops, customer_support_office)

# ApplicationComponent serves BusinessActor
serves(sales_force_automation, sales_contractor)
serves(customer_relationship_management, customer_support_office)
serves(enterprise_resource_planning, production_office)
serves(accounting, accounting_office)
serves(asset_management, accounting_office)
serves(asset_management, administration_office)
serves(human_resource_management, human_resource_office)
serves(accounting, administration_office)
serves(accounting, human_resource_office)
serves(accounting, customer_support_office)
serves(accounting, production_office)
serves(asset_management, customer_support_office)
serves(asset_management, production_office)
serves(asset_management, human_resource_office)
serves(human_resource_management, customer_support_office)
serves(human_resource_management, production_office)
serves(human_resource_management, accounting_office)
serves(human_resource_management, administration_office)
serves(human_resource_management, executives)
serves(asset_management, executives)
serves(accounting, executives)
serves(enterprise_resource_planning, executives)
serves(customer_relationship_management, executives)
serves(sales_force_automation, executives)
serves(communication, customer_support_office)
serves(communication, production_office)
serves(communication, accounting_office)
serves(communication, administration_office)
serves(communication, human_resource_office)
serves(communication, executives)

# ApplicationComponent accesses DataObject
accesses(sales_force_automation, customers)
accesses(customer_relationship_management, sales_contracts)
accesses(customer_relationship_management, customers)
accesses(enterprise_resource_planning, sales_contracts)
accesses(enterprise_resource_planning, materials)
accesses(accounting, assets)
accesses(enterprise_resource_planning, assets)
accesses(accounting, materials)
accesses(accounting, sales_contracts)
accesses(human_resource_management, human_resources)
accesses(accounting, human_resources)
accesses(asset_management, assets)
accesses(enterprise_resource_planning, purchase_contracts)
accesses(accounting, purchase_contracts)
accesses(sales_force_automation, sales_contracts)
accesses(communication, messages)
accesses(communication, documents)

# Device realizes ApplicationComponent
realizes(public_web_server, sales_force_automation)
realizes(public_web_server, customer_relationship_management)
realizes(internal_web_server, enterprise_resource_planning)
realizes(internal_web_server, accounting)
realizes(internal_web_server, asset_management)
realizes(internal_web_server, human_resource_management)
realizes(communication_cloud_service, communication)

# Artifact realizes DataObject
realizes(message_files, messages)
realizes(document_files, documents)
realizes(database, customers)
realizes(database, sales_contracts)
realizes(database, materials)
realizes(database, purchase_contracts)
realizes(database, assets)
realizes(database, human_resources)

# Device serves Device
serves(customer_application_server, public_web_server)
serves(database_server, customer_application_server)
serves(database_server, internal_application_server)
serves(internal_application_server, internal_web_server)
serves(internal_web_server, managed_laptops)
serves(internal_web_server, secured_laptops)

# Device isAssignedTo Artifact
isAssignedTo(communication_cloud_service, message_files)
isAssignedTo(communication_cloud_service, document_files)
isAssignedTo(database_server, database)

# Device flowsTo CommunicationNetwork
flowsTo(communication_cloud_service, the_internet)
flowsTo(public_web_server, public_lan)
flowsTo(customer_application_server, private_lan)
flowsTo(internal_application_server, private_lan)
flowsTo(internal_web_server, private_lan)
flowsTo(customer_device, the_internet)
flowsTo(unmanaged_mobile_phones, the_internet)
flowsTo(unmanaged_laptops, the_internet)
flowsTo(managed_mobile_phones, the_internet)
flowsTo(managed_laptops, the_internet)
flowsTo(secured_mobile_phones, the_internet)
flowsTo(secured_laptops, the_internet)
flowsTo(secured_laptops, private_lan)
flowsTo(managed_laptops, private_lan)

# CommunicationNetwork flowsTo Device
flowsTo(the_internet, communication_cloud_service)
flowsTo(the_internet, public_web_server)
flowsTo(public_lan, customer_application_server)
flowsTo(private_lan, database_server)
flowsTo(private_lan, internal_application_server)
flowsTo(private_lan, internal_web_server)




#-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-#
# Supplemental information to the architecture, including the access control list
#-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-#

isPowerful(customer_device)
isPowerful(laptops_for_sales)
isPowerful(laptops_for_customer_support)
isPowerful(laptops_for_production)
isPowerful(laptops_for_accounting)
isPowerful(laptops_for_administration)
isPowerful(laptops_for_human_resource)
isPowerful(laptops_for_executive)

readFrom(sales_contractor, sales_force_automation, customers)
readFrom(sales_contractor, sales_force_automation, sales_contracts)
writeTo(sales_contractor, sales_force_automation, customers)
writeTo(sales_contractor, sales_force_automation, sales_contracts)

readFrom(customer_support_office, customer_relationship_management, customers)
readFrom(customer_support_office, customer_relationship_management, sales_contracts)
writeTo(customer_support_office, customer_relationship_management, customers)
writeTo(customer_support_office, customer_relationship_management, sales_contracts)
readFrom(customer_support_office, asset_management, assets)
readFrom(customer_support_office, human_resource_management, human_resources)
readFrom(customer_support_office, communication, documents)
readFrom(customer_support_office, communication, messages)
writeTo(customer_support_office, asset_management, assets)
writeTo(customer_support_office, human_resource_management, human_resources)
writeTo(customer_support_office, communication, documents)
writeTo(customer_support_office, communication, messages)

readFrom(production_office, enterprise_resource_planning, sales_contracts)
readFrom(production_office, enterprise_resource_planning, materials)
readFrom(production_office, enterprise_resource_planning, purchase_contracts)
readFrom(production_office, enterprise_resource_planning, assets)
writeTo(production_office, enterprise_resource_planning, sales_contracts)
writeTo(production_office, enterprise_resource_planning, materials)
writeTo(production_office, enterprise_resource_planning, purchase_contracts)
writeTo(production_office, enterprise_resource_planning, assets)
readFrom(production_office, asset_management, assets)
readFrom(production_office, human_resource_management, human_resources)
readFrom(production_office, communication, documents)
readFrom(production_office, communication, messages)
writeTo(production_office, asset_management, assets)
writeTo(production_office, human_resource_management, human_resources)
writeTo(production_office, communication, documents)
writeTo(production_office, communication, messages)

readFrom(accounting_office, accounting, sales_contracts)
readFrom(accounting_office, accounting, materials)
readFrom(accounting_office, accounting, purchase_contracts)
readFrom(accounting_office, accounting, assets)
readFrom(accounting_office, accounting, human_resources)
writeTo(accounting_office, accounting, sales_contracts)
writeTo(accounting_office, accounting, materials)
writeTo(accounting_office, accounting, purchase_contracts)
writeTo(accounting_office, accounting, assets)
readFrom(accounting_office, asset_management, assets)
readFrom(accounting_office, human_resource_management, human_resources)
readFrom(accounting_office, communication, documents)
readFrom(accounting_office, communication, messages)
writeTo(accounting_office, asset_management, assets)
writeTo(accounting_office, human_resource_management, human_resources)
writeTo(accounting_office, communication, documents)
writeTo(accounting_office, communication, messages)

readFrom(administration_office, asset_management, assets)
readFrom(administration_office, human_resource_management, human_resources)
readFrom(administration_office, communication, documents)
readFrom(administration_office, communication, messages)
writeTo(administration_office, asset_management, assets)
writeTo(administration_office, human_resource_management, human_resources)
writeTo(administration_office, communication, documents)
writeTo(administration_office, communication, messages)

readFrom(human_resource_office, asset_management, assets)
readFrom(human_resource_office, human_resource_management, human_resources)
readFrom(human_resource_office, communication, documents)
readFrom(human_resource_office, communication, messages)
writeTo(human_resource_office, asset_management, assets)
writeTo(human_resource_office, human_resource_management, human_resources)
writeTo(human_resource_office, communication, documents)
writeTo(human_resource_office, communication, messages)

readFrom(executives, sales_force_automation, customers)
readFrom(executives, sales_force_automation, sales_contracts)
readFrom(executives, customer_relationship_management, customers)
readFrom(executives, customer_relationship_management, sales_contracts)
readFrom(executives, enterprise_resource_planning, sales_contracts)
readFrom(executives, enterprise_resource_planning, materials)
readFrom(executives, enterprise_resource_planning, purchase_contracts)
readFrom(executives, accounting, purchase_contracts)
readFrom(executives, asset_management, assets)
readFrom(executives, human_resource_management, human_resources)
readFrom(executives, communication, documents)
readFrom(executives, communication, messages)
writeTo(executives, asset_management, assets)
writeTo(executives, human_resource_management, human_resources)
writeTo(executives, communication, documents)
writeTo(executives, communication, messages)



#-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-#
# Attack templates
#-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-#


# # # # # # # # # # # # # # # # # # # # #
# Incidents in technology layer
# # # # # # # # # # # # # # # # # # # # #

# Non-redundant device can break.
broken(Device)
    :- _Device(Device), noRedundancy(Device).

# A device used by a malicious actor can be a point of attack.
attacked(Device)
    :- _Device(Device), _BusinessActor(BusinessActor), serves(Device, BusinessActor), isMalicious(BusinessActor).

# A powerful device used by a malicious actor can be a point of DoS attack.
overloaded(Device)
    :- _Device(Device), _BusinessActor(BusinessActor), serves(Device, BusinessActor), isPowerful(Device), isMalicious(BusinessActor).

# A device used by a vulnerable actor without protection can be compromised by malwares.
compromised(Device)
    :- _Device(Device), _BusinessActor(BusinessActor), serves(Device, BusinessActor), noProtection(Device), isVulnerable(BusinessActor).

# A communication network entity is a kind of device.
_Device(CommunicationNetwork)
    :- _CommunicationNetwork(CommunicationNetwork).

# Any broken device becomes unavailable.
unavailable(Device)
    :- _Device(Device), broken(Device).

# Any artifact on an unavailable device is also unavailable.
unavailable(Artifact)
    :- _Device(Device), _Artifact(Artifact), isAssignedTo(Device, Artifact), unavailable(Device).

# When the intermediate device on the adjacent network nodes is unavailable, it makes the dependent device unavailable.
# * Note that this template cannot handle well when there are multiple alternative routes.
unavailable(Device1)
    :- _Device(Device1), _Device(Net), _Device(Device2), serves(Device2, Device1), flowsTo(Device1, Net), flowsTo(Net, Device2), unavailable(Net).

# Any attack can propagate when the adjacent node is attacked and itself has no protection.
attacked(Device2)
    :- _Device(Device1), _Device(Device2), flowsTo(Device1, Device2), noProtection(Device2), attacked(Device1).

# Any attack can propagate when the adjacent node is attacked and itself is vulnerable.
attacked(Device2)
    :- _Device(Device1), _Device(Device2), flowsTo(Device1, Device2), isVulnerable(Device2), attacked(Device1).

# A device that is connected from a compromised device becomes an attack target.
attacked(Device2)
    :- _Device(Device1), _Device(Net), _Device(Device2), serves(Device2, Device1), flowsTo(Device1, Net), flowsTo(Net, Device2), compromised(Device1).

# A device can be compromised when it is vulnerable and attacked.
compromised(Device)
    :- _Device(Device), isVulnerable(Device), attacked(Device).

# Any compromised device becomes unavailable.
unavailable(Device)
    :- _Device(Device), compromised(Device).

# Any device becomes unavailable when its dependent device is unavailable.
unavailable(Device1)
    :- _Device(Device1), _Device(Device2), serves(Device2, Device1), unavailable(Device2).

# Any device accessible from a device under DoS attack can also be a DoS attack target.
overloaded(Device2)
    :- _Device(Device1), _Device(Device2), flowsTo(Device1, Device2), attacked(Device2), overloaded(Device1).

# Any device under DoS attack becomes unavailable when it is not load-balanced.
unavailable(Device)
    :- _Device(Device), noLoadBalancing(Device), overloaded(Device).


# Any artifact on a compromised device can leak.
leaked(Artifact)
    :- _Device(Device), _Artifact(Artifact), isAssignedTo(Device, Artifact), compromised(Device).


# Any artifact on a compromised device can be tampered.
tampered(Artifact)
    :- _Device(Device), _Artifact(Artifact), isAssignedTo(Device, Artifact), compromised(Device).




# # # # # # # # # # # # # # # # # # # # #
# Incidents in application layer
# # # # # # # # # # # # # # # # # # # # #

# Any application stops when its dependent device is unavailable.
halted(ApplicationComponent)
    :- _Device(Device), _ApplicationComponent(ApplicationComponent), realizes(Device, ApplicationComponent), unavailable(Device).

# Any data becomes inaccessible when its dependent artifact is unavailable.
unavailable(DataObject)
    :- _Artifact(Artifact), _DataObject(DataObject), realizes(Artifact, DataObject), unavailable(Artifact).

# Any application stops when its accessing data is inaccessible.
halted(ApplicationComponent)
    :- _ApplicationComponent(ApplicationComponent), _DataObject(DataObject), accesses(ApplicationComponent, DataObject), unavailable(DataObject).


# Any non-encrypted data that is represented on a leaked artifact can also leak.
leaked(DataObject)
    :- _Artifact(Artifact), _DataObject(DataObject), realizes(Artifact, DataObject), leaked(Artifact), noEncryption(Artifact).


# Any data that is represented on a tampered artifact can also be tampered.
tampered(DataObject)
    :- _Artifact(Artifact), _DataObject(DataObject), realizes(Artifact, DataObject), tampered(Artifact).



# # # # # # # # # # # # # # # # # # # # #
# Incidents in business layer
# # # # # # # # # # # # # # # # # # # # #

# Any business can stop when its dependent device becomes unavailable.
interrupted(BusinessActor)
    :- _Device(Device), _BusinessActor(BusinessActor), serves(Device, BusinessActor), unavailable(Device).

# Any business can stop when its dependent application becomes halted.
interrupted(BusinessActor)
    :- _ApplicationComponent(ApplicationComponent), _BusinessActor(BusinessActor), serves(ApplicationComponent, BusinessActor), halted(ApplicationComponent).


# Any data readable from a compromised device can leak through cyber espionage.
leaked(DataObject)
    :- _Device(Device), _BusinessActor(BusinessActor), _DataObject(DataObject), serves(Device, BusinessActor),
       readFrom(BusinessActor, ApplicationComponent, DataObject), compromised(Device).


# Any data writable from a compromised device can be tampered through cyber espionage.
tampered(DataObject)
    :- _Device(Device), _BusinessActor(BusinessActor), _DataObject(DataObject), serves(Device, BusinessActor),
       writeTo(BusinessActor, ApplicationComponent, DataObject), compromised(Device).

# Tampered purchase contracts can lead to wrong deliveries.
productsSentToWrongPlace()
    :- tampered(purchase_contracts).

# Tampered sales contracts can lead to wrong deliveries.
productsSentToWrongPlace()
    :- tampered(sales_contracts).

# Tampered purchase contracts can lead to wrong payments.
moneySentToWrongAccount()
    :- tampered(purchase_contracts).

# Tampered payroll data can lead to wrong payments.
moneySentToWrongAccount()
    :- tampered(human_resources).

# Tampered bill-of-materials data can lead to physical accidents in factories.
accidentsOccur()
    :- tampered(materials).

# Tampered instruments data can lead to physical accidents in factories.
accidentsOccur()
    :- tampered(assets).



# # # # # # # # # # # # # # # # # # # # #
# Social engineering
# # # # # # # # # # # # # # # # # # # # #

# Leaked human resource data enables sophisticated forgery of phishing messages.
forged(messages)
    :- leaked(human_resources).

# Any vulnerable actor can leak information when receiving sophisticated phishing messages.
leaked(DataObject)
    :- _BusinessActor(BusinessActor), _ApplicationComponent(ApplicationComponent), _DataObject(DataObject),
       readFrom(BusinessActor, ApplicationComponent, DataObject), readFrom(BusinessActor, communication, messages), isVulnerable(BusinessActor), forged(messages).


#-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-#
# Vulnerabilities and threats
#-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-#

# Insider threats
isMalicious(customer)
isMalicious(sales_contractor)
isMalicious(customer_support_office)
isMalicious(production_office)
isMalicious(accounting_office)
isMalicious(administration_office)
isMalicious(human_resource_office)
isMalicious(executives)


# Client-side vulnerabilities
isVulnerable(sales_contractor)
isVulnerable(customer_support_office)
isVulnerable(production_office)
isVulnerable(accounting_office)
isVulnerable(administration_office)
isVulnerable(human_resource_office)
isVulnerable(executives)

isVulnerable(unmanaged_mobile_phones)
noProtection(unmanaged_mobile_phones)
noRedundancy(unmanaged_mobile_phones)

isVulnerable(managed_mobile_phones)
noRedundancy(managed_mobile_phones)

isVulnerable(secured_mobile_phones)


isVulnerable(unmanaged_laptops)
noProtection(unmanaged_laptops)
noRedundancy(unmanaged_laptops)

isVulnerable(managed_laptops)
noRedundancy(managed_laptops)

isVulnerable(secured_laptops)


# Network vulnerabilities
noRedundancy(public_lan)
noLoadBalancing(public_lan)

noRedundancy(private_lan)
noLoadBalancing(private_lan)

isVulnerable(vpn)
noProtection(vpn)

noProtection(the_internet)


# Server-side vulnerabilities
isVulnerable(public_web_server)
noRedundancy(public_web_server)
noProtection(public_web_server)
noLoadBalancing(public_web_server)

isVulnerable(customer_application_server)
noRedundancy(customer_application_server)
noProtection(customer_application_server)
noLoadBalancing(customer_application_server)

isVulnerable(database_server)
noRedundancy(database_server)
noProtection(database_server)
noLoadBalancing(database_server)

isVulnerable(internal_application_server)
noRedundancy(internal_application_server)
noProtection(internal_application_server)
noLoadBalancing(internal_application_server)

isVulnerable(internal_web_server)
noRedundancy(internal_web_server)
noProtection(internal_web_server)
noLoadBalancing(internal_web_server)

noEncryption(database)


