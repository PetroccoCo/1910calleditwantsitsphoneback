"""
SIP library using pjsua2 (pjproject)

OK, so this code seems to be directly lifted from pjproject's TRAC page sample
code. That code is awful, unpythonic (they redefine str and len, amateurs) and
ALSO pretty undocumented. So, great fun.
"""


from pjsua import Lib, AuthCred, AccountConfig, LogConfig, CallCallback, \
    AccountCallback, TransportType, MediaState, MediaConfig, UAConfig, TransportConfig
import threading

def log(level, string, length):
    """
    Log any event.
    """
    print "[DEBUG]", string.rstrip("\n")


class SipClient(object):
    """
    Class to represent a SIP connection.
    """
    # TODO: Handle multiple Account and CallCallBack objects for 2-account use

    hostname = None
    username = None
    password = None
    current_call = None

    account_config = None
    login_object = None

    account_handler = None
    call_handler = None

    lib = None

    def __init__(self):
        self.lib = Lib()
        my_ua_cfg = UAConfig()
        my_ua_cfg.nameserver = ['8.8.8.8', '8.8.4.4']
        my_ua_cfg.stun_host = "stun.ekiga.net"
        my_media_cfg = MediaConfig()
        my_media_cfg.enable_ice = False

        self.lib.init(ua_cfg=my_ua_cfg, media_cfg=my_media_cfg, log_cfg=LogConfig(level=4, callback=log))

        # Create UDP transport which listens to any available port
        self.transport = self.lib.create_transport(TransportType.UDP, TransportConfig(0))
    
    def set_audio(self, earpiece_device, mouthpiece_device):
        """
        Use ALSA audio name to select sound device for pjsip.
        """
        earpiece_index = 0
        mouthpiece_index = 0

        devices = self.lib.enum_snd_dev()
        for index, device in enumerate(devices):
            print "[INFO] got earpiece", device.name, index
            if device.name == earpiece_device:
                print "[INFO] got earpiece", device.name, index
                earpiece_index = index
                break
        else:
            print "[WARNING] no earpiece found. Defaulting to:", \
                devices[0].name

        for index, device in enumerate(devices):
            if device.name == mouthpiece_device:
                print "[INFO] got mouthpiece", device.name, index
                mouthpiece_index = index
                break
        else:
            print "[WARNING] no mouthpiece found. Defaulting to:", \
                devices[0].name

        self.lib.set_snd_dev(mouthpiece_index, earpiece_index)

    def login(self, hostname, username, password, domain=''):
        """
        Connect to a SIP server using the provided credentials.
        """
        self.lib.start()
        self.hostname = 'pgisandbox.gm.ucaas.com'
        #self.account_config = AccountConfig(domain, hostname, username, password)
        self.account_config = AccountConfig()
        self.account_config.reg_uri  = "sip:sip.uc.globalmeet.com"
        self.account_config.id = "sip:user_DXDVYC8uYg@pgisandbox.gm.ucaas.com"
        self.account_config.auth_cred = [AuthCred("pgisandbox.gm.ucaas.com", "user_DXDVYC8uYg", "9G4WpvuX9V6J")]

        self.login_object = self.lib.create_account(self.account_config,
                                                    cb=self.account_handler)

        self.account_handler.wait()

        print "\n"
        print "Registration complete, status=", self.login_object.info().reg_status, \
              "(" + self.login_object.info().reg_reason + ")"



    def dial(self, number):
        """
        Place an outgoing call.
        """
        destination = "sip:%s@%s" % (number, self.hostname)
        self.current_call = self.login_object.make_call(
            destination, cb=self.call_handler)

    def logout(self):
        """
        Safely end the SIP connection and close the pjsip thread.
        """
        self.lib.destroy()
        self.lib = None

    def register_callbacks(self, call_handler, account_handler):
        """
        Register callback functions to calling application
        """
        self.call_handler = call_handler
        self.account_handler = account_handler


class CallHandler(CallCallback):
    """
    This is a callback function that receives alerts from the SIP client about
    the status of calls. It should callback to TelephoneDaemon (via SipClient)
    to allow the playing of earpiece tones appropriate to each state.
    """

    call = None

    remote_busy = None
    connected = None
    remote_hangup = None
    call_dropped = None
    call_failed = None

    def __init__(self, call=None):
        CallCallback.__init__(self, call)  # Use Super() when fixed.

    def on_state(self):
        """
        Essentially a logging update that alerts whenever a signal is received
        """
        print "Call is %s" % self.call.info().state_text
        print "Last code = %s" % self.call.info().last_code
        print "Last reason = %s" % self.call.info().last_reason

    def on_media_state(self):
        """
        React to a change in the state of the transport, e.g. connected,
        dropped, rejected, etc.
        """
        if self.call.info().media_state == MediaState.ACTIVE:
            self.connected(self.call)

    def register_callbacks(self, remote_busy, connected,
                           remote_hangup, call_dropped, call_failed):
        """
        Register callback functions to calling application
        """
        self.remote_busy = remote_busy
        self.connected = connected
        self.remote_hangup = remote_hangup
        self.call_dropped = call_dropped
        self.call_failed = call_failed


class AccountHandler(AccountCallback):
    """
    I don't know what this is either! Some sort of subclass? It seems weird
    that it would handle both account registration AND incoming calls?
    """

    logged_in = None
    unregistered = None
    incoming_call = None

    def __init__(self, account=None):
        print "Account handler created"
        AccountCallback.__init__(self, account)  # Use Super() when fixed.

    def on_incoming_call(self, call):
        """
        Pass the call object back to the phone application.
        """
        print "Incoming call!!! %s" % call
        self.incoming_call(call)

    def wait(self):
        self.sem = threading.Semaphore(0)
        self.sem.acquire()

    def on_reg_state(self):
        if self.sem:
            if self.account.info().reg_status >= 200:
                self.sem.release()

    def register_callbacks(self, registered, unregistered, incoming_call):
        """
        Register callback functions to calling application
        """
        print "register_callback"

        self.incoming_call = incoming_call
        self.registered = registered
        self.unregistered = unregistered


