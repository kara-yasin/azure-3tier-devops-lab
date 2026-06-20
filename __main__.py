import pulumi
from pulumi_azure_native import resources, network, compute

config = pulumi.Config("azure-native")
location = config.require("location")

resource_group = resources.ResourceGroup("rg-3tier-devops-lab",
    resource_group_name="rg-3tier-devops-lab",
    location=location,
)


vnet = network.VirtualNetwork("vnet-3tier-lab",
    resource_group_name=resource_group.name,
    virtual_network_name="vnet-3tier-lab",
    location=location,
    address_space=network.AddressSpaceArgs(
        address_prefixes=["10.0.0.0/16"],
    ),
    opts=pulumi.ResourceOptions(ignore_changes=[
        "encryption",
        "privateEndpointVNetPolicies",
        "subnets",
    ]),
)


web_subnet = network.Subnet("snet-web",
    resource_group_name=resource_group.name,
    virtual_network_name=vnet.name,
    subnet_name="snet-web",
    address_prefixes=["10.0.1.0/24"],
    default_outbound_access=False,
    opts=pulumi.ResourceOptions(ignore_changes=["name", "type"]),
)

app_subnet = network.Subnet("snet-app",
    resource_group_name=resource_group.name,
    virtual_network_name=vnet.name,
    subnet_name="snet-app",
    address_prefixes=["10.0.2.0/24"],
    default_outbound_access=False,
    opts=pulumi.ResourceOptions(ignore_changes=["name", "type"]),
)

db_subnet = network.Subnet("snet-db",
    resource_group_name=resource_group.name,
    virtual_network_name=vnet.name,
    subnet_name="snet-db",
    address_prefixes=["10.0.3.0/24"],
    default_outbound_access=False,
    opts=pulumi.ResourceOptions(ignore_changes=["name", "type"]),
)


network_interface = network.NetworkInterface("vm-app-prod108",
    resource_group_name=resource_group.name,
    network_interface_name="vm-app-prod108",
    location=location,
    enable_accelerated_networking=True,
    network_security_group=network.NetworkSecurityGroupArgs(
        id="/subscriptions/08a2c138-cd3e-49bd-a43c-cad420cd028d/resourceGroups/rg-3tier-devops-lab/providers/Microsoft.Network/networkSecurityGroups/vm-app-prod-nsg",
    ),
    ip_configurations=[network.NetworkInterfaceIPConfigurationArgs(
        name="ipconfig1",
        subnet=network.SubnetArgs(id=app_subnet.id),
        private_ip_allocation_method=network.IPAllocationMethod.DYNAMIC,
    )],
    opts=pulumi.ResourceOptions(ignore_changes=[
        "auxiliaryMode",
        "auxiliarySku",
        "disableTcpStateTracking",
        "enableIPForwarding",
        "nicType",
        "ipConfigurations",
    ]),
)


vm = compute.VirtualMachine("vm-app-prod",
    resource_group_name=resource_group.name,
    vm_name="vm-app-prod",
    location=location,
    zones=["3"],
    hardware_profile=compute.HardwareProfileArgs(
        vm_size="Standard_B2ts_v2",
    ),
    storage_profile=compute.StorageProfileArgs(
        image_reference=compute.ImageReferenceArgs(
            publisher="Canonical",
            offer="ubuntu-24_04-lts",
            sku="server",
            version="latest",
        ),
        os_disk=compute.OSDiskArgs(
            name="vm-app-prod_OsDisk_1_567de1f95c464e319a7f98d95ce51be1",
            create_option=compute.DiskCreateOptionTypes.FROM_IMAGE,
            caching=compute.CachingTypes.READ_WRITE,
            disk_size_gb=30,
            managed_disk=compute.ManagedDiskParametersArgs(
                storage_account_type=compute.StorageAccountTypes.PREMIUM_LRS,
            ),
        ),
    ),
    os_profile=compute.OSProfileArgs(
        computer_name="vm-app-prod",
        admin_username="azureuser",
        linux_configuration=compute.LinuxConfigurationArgs(
            disable_password_authentication=True,
        ),
    ),
    network_profile=compute.NetworkProfileArgs(
        network_interfaces=[compute.NetworkInterfaceReferenceArgs(
            id=network_interface.id,
            primary=True,
            delete_option=compute.DeleteOptions.DETACH,
        )],
    ),
    diagnostics_profile=compute.DiagnosticsProfileArgs(
        boot_diagnostics=compute.BootDiagnosticsArgs(
            enabled=True,
        ),
    ),
    security_profile=compute.SecurityProfileArgs(
        security_type=compute.SecurityTypes.TRUSTED_LAUNCH,
        uefi_settings=compute.UefiSettingsArgs(
            secure_boot_enabled=True,
            v_tpm_enabled=True,
        ),
    ),
    opts=pulumi.ResourceOptions(ignore_changes=[
        "osProfile",
        "storageProfile",
        "networkProfile",
        "additionalCapabilities",
        "placement",
    ]),
)


pulumi.export("resource_group_name", resource_group.name)
pulumi.export("vnet_name", vnet.name)
