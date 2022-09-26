# -*- mode: python; python-indent: 4 -*-
import ncs
from ncs.application import Service
import ipaddress

# ------------------------
# SERVICE CALLBACK EXAMPLE
# ------------------------
class ServiceCallbacks(Service):

    # The create() callback is invoked inside NCS FASTMAP and
    # must always exist.
    @Service.create
    def cb_create(self, tctx, root, service, proplist):
        self.log.info('Service create(service=', service._path, ')')

        ipcount = 0
        vars = ncs.template.Variables()                    # Initiate variables container object
        vars.add('INTERFACE_ID', service.interface_id)     # Relay some variables over from yang to variables container
        vars.add('ACL_NAME', service.acl_name)
        vars.add('ACL_LINE', service.acl_line)
        vars.add('ACL_SUBNET_ADDRESS', service.acl_subnet_address)

        for dev in service.device:                         # Loop over the devices listed in the service instance instruction
            self.log.info('device: ', dev)
            vars.add('DEVICE', dev)                        # Fill in the DEVICE variable
            # IPAM:
            subnet = service.interface_subnet              # Calculate the IP address to be used for the interface
            interface_subnet_int = int(ipaddress.ip_address(subnet))
            interface_ip = str(ipaddress.IPv4Address(interface_subnet_int+ipcount*4+1))
            self.log.info('Interface IP: ', interface_ip)
            vars.add('INTERFACE_IP', interface_ip)

            ipcount = ipcount + 1                         # Increase counter
            template = ncs.template.Template(service)
            template.apply('AclService2-template', vars)  # Apply variables to template and run it

    # The pre_modification() and post_modification() callbacks are optional,
    # and are invoked outside FASTMAP. pre_modification() is invoked before
    # create, update, or delete of the service, as indicated by the enum
    # ncs_service_operation op parameter. Conversely
    # post_modification() is invoked after create, update, or delete
    # of the service. These functions can be useful e.g. for
    # allocations that should be stored and existing also when the
    # service instance is removed.

    # @Service.pre_lock_create
    # def cb_pre_lock_create(self, tctx, root, service, proplist):
    #     self.log.info('Service plcreate(service=', service._path, ')')

    # @Service.pre_modification
    # def cb_pre_modification(self, tctx, op, kp, root, proplist):
    #     self.log.info('Service premod(service=', kp, ')')

    # @Service.post_modification
    # def cb_post_modification(self, tctx, op, kp, root, proplist):
    #     self.log.info('Service postmod(service=', kp, ')')


# ---------------------------------------------
# COMPONENT THREAD THAT WILL BE STARTED BY NCS.
# ---------------------------------------------
class Main(ncs.application.Application):
    def setup(self):
        # The application class sets up logging for us. It is accessible
        # through 'self.log' and is a ncs.log.Log instance.
        self.log.info('Main RUNNING')

        # Service callbacks require a registration for a 'service point',
        # as specified in the corresponding data model.
        #
        self.register_service('AclService2-servicepoint', ServiceCallbacks)

        # If we registered any callback(s) above, the Application class
        # took care of creating a daemon (related to the service/action point).

        # When this setup method is finished, all registrations are
        # considered done and the application is 'started'.

    def teardown(self):
        # When the application is finished (which would happen if NCS went
        # down, packages were reloaded or some error occurred) this teardown
        # method will be called.

        self.log.info('Main FINISHED')
