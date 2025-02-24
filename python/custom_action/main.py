# -*- mode: python; python-indent: 4 -*-
import ncs
from ncs.application import Service
from ncs.dp import Action


# ---------------
# ACTIONS EXAMPLE
# ---------------
class CheckIFAction(Action):
    @Action.action
    def cb_action(self, uinfo, name, kp, input, output, trans):
        self.log.info('action name: ', name)
        self.log.info('action input.device: ', input.device)

        dev_name = input.device

        root = ncs.maagic.get_root(trans)
        device = root.ncs__devices.device[dev_name]
        error_string = ''
        
        try:
            if ('tailf-ned-cisco-ios-xr-stats', '') in device.live_status.yanglib__modules_state.module:
                self.log.info(dev_name, ' is a cisco-iosxr device')
                command = "show interfaces brief"
                live_input = device.live_status.cisco_ios_xr_stats__exec.any.get_input()
                live_input.args = [command]
                live_output = device.live_status.cisco_ios_xr_stats__exec.any(live_input)
                self.log.info("live_output: ", live_output.result)
            elif ('tailf-ned-cisco-ios-stats', '') in device.live_status.yanglib__modules_state.module:
                self.log.info(dev_name, ' is a cisco-ios device')
                command = "show ip interface brief"
                live_input = device.live_status.ios_stats__exec.any.get_input()
                live_input.args = [command]
                live_output = device.live_status.ios_stats__exec.any(live_input)
                self.log.info("live_output: ", live_output.result)
            elif ('tailf-ned-cisco-asa-stats', '') in device.live_status.yanglib__modules_state.module:
                self.log.info(dev_name, ' is a cisco-asa device')
                command = "show interface ip brief"
                live_input = device.live_status.asa_stats__exec.any.get_input()
                live_input.args = [command]
                live_output = device.live_status.asa_stats__exec.any(live_input)
                self.log.info("live_output: ", live_output.result)
                     
        except Exception as e:
            self.log.info(dev_name, " ERROR: ", str(e))
            error_string = "ERROR: " + str(e)

        # check if its a string or an object.
        if error_string:
            output.result = error_string
        else:
            output.result = live_output.result


# ------------------------
# SERVICE CALLBACK EXAMPLE
# ------------------------
class ServiceCallbacks(Service):

    # The create() callback is invoked inside NCS FASTMAP and
    # must always exist.
    @Service.create
    def cb_create(self, tctx, root, service, proplist):
        self.log.info('Service create(service=', service._path, ')')


    # The pre_modification() and post_modification() callbacks are optional,
    # and are invoked outside FASTMAP. pre_modification() is invoked before
    # create, update, or delete of the service, as indicated by the enum
    # ncs_service_operation op parameter. Conversely
    # post_modification() is invoked after create, update, or delete
    # of the service. These functions can be useful e.g. for
    # allocations that should be stored and existing also when the
    # service instance is removed.

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
        self.register_service('custom-action-servicepoint', ServiceCallbacks)

        # When using actions, this is how we register them:
        #
        self.register_action('checkif', CheckIFAction)

        # If we registered any callback(s) above, the Application class
        # took care of creating a daemon (related to the service/action point).

        # When this setup method is finished, all registrations are
        # considered done and the application is 'started'.

    def teardown(self):
        # When the application is finished (which would happen if NCS went
        # down, packages were reloaded or some error occurred) this teardown
        # method will be called.

        self.log.info('Main FINISHED')
