import logging
import os
import shutil
import time

import undetected_chromedriver as uc

logger = logging.getLogger("uc")
logger.setLevel(logging.getLogger().getEffectiveLevel())


class CustomUndetectedChromeDriver(uc.Chrome):
    """
    Class for fix OSError: [WinError 6] in undetected_chromedriver library
    """

    def __init__(self, version_main=None, options=None, headless=False, **kwargs):
        super().__init__(version_main=version_main, options=options, headless=headless, **kwargs)
        self.version_main = version_main
        self.options = options
        self.headless = headless

    def quit(self):
        try:
            self.service.process.kill()
            logger.debug("webdriver process ended")
        except (AttributeError, RuntimeError, OSError):
            pass
        try:
            self.reactor.event.set()
            logger.debug("shutting down reactor")
        except AttributeError:
            pass
        try:
            os.kill(self.browser_pid, 15)
            logger.debug("gracefully closed browser")
        except Exception as e:  # noqa
            pass
        if (
                hasattr(self, "keep_user_data_dir")
                and hasattr(self, "user_data_dir")
                and not self.keep_user_data_dir
        ):
            for _ in range(5):
                try:
                    shutil.rmtree(self.user_data_dir, ignore_errors=False)
                except FileNotFoundError:
                    pass
                except (RuntimeError, OSError, PermissionError) as e:
                    logger.debug(
                        "When removing the temp profile, a %s occured: %s\nretrying..."
                        % (e.__class__.__name__, e)
                    )
                else:
                    logger.debug("successfully removed %s" % self.user_data_dir)
                    break

                # Skip OSError: [WinError 6]
                try:
                    time.sleep(0.1)
                except OSError:
                    pass

        # dereference patcher, so patcher can start cleaning up as well.
        # this must come last, otherwise it will throw 'in use' errors
        self.patcher = None
