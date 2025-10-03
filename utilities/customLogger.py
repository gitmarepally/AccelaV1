import logging
import os

class LogGen():
    @staticmethod
    def loggen():
        path=os.path.abspath(os.curdir)
        log_dir=os.path.join(path,'logs')
        os.makedirs(log_dir, exist_ok=True)

        log_file = os.path.join(log_dir, "automation.log")

        # create logger with a name (avoid root logger issues)
        logger = logging.getLogger("automation")
        logger.setLevel(logging.DEBUG)

        # if handlers already exist, don't add duplicate ones
        if not logger.handlers:
            file_handler = logging.FileHandler(log_file, mode="w")
            formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s",
                datefmt="%d/%m/%Y %I:%M:%S %p"
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        return logger








# import logging
# import os
#
# class LogGen:
#     @staticmethod
#     def loggen():
#         base = os.path.abspath(os.curdir)
#         log_dir = os.path.join(base, "logs")
#         os.makedirs(log_dir, exist_ok=True)
#
#         log_file = os.path.join(log_dir, "automation.log")
#
#         logger = logging.getLogger("automation")
#         logger.setLevel(logging.DEBUG)
#         logger.propagate = False
#
#         if not logger.handlers:
#             file_handler = logging.FileHandler(log_file, mode="w")
#             file_handler.setLevel(logging.DEBUG)
#             formatter = logging.Formatter(
#                 "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#                 datefmt="%d/%m/%Y %I:%M:%S %p"
#             )
#             file_handler.setFormatter(formatter)
#             logger.addHandler(file_handler)
#
#         return logger
#
#
# if __name__ == "__main__":
#     logger = LogGen.loggen()
#
#     # write some test logs
#     logger.debug("This is a DEBUG message (should appear in file).")
#     logger.info("This is an INFO message.")
#     logger.warning("This is a WARNING message.")
#     logger.error("This is an ERROR message.")
#     logger.critical("This is a CRITICAL message.")
#
#     print("Logs written to logs/automation.log")



# import logging
# import os
#
# class LogGen:
#     @staticmethod
#     def loggen():
#         base = os.path.abspath(os.curdir)
#         log_dir = os.path.join(base, "logs")
#         os.makedirs(log_dir, exist_ok=True)
#
#         path = os.path.join(log_dir, "automation.log")
#         path_abs = os.path.abspath(path)
#
#         logger = logging.getLogger("automation_logger")
#         logger.setLevel(logging.DEBUG)
#         logger.propagate = False
#         #logging.basicConfig(filename=path, format='%(asctime)s:%(levelname)s:%(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
#
#         # check if a FileHandler for this exact path already exists
#         found_fh = False
#         for h in logger.handlers:
#             if isinstance(h, logging.FileHandler):
#                 # file handlers have baseFilename attribute
#                 try:
#                     if os.path.abspath(getattr(h, "baseFilename", "")) == path_abs:
#                         found_fh = True
#                 except Exception:
#                     pass
#
#         if not found_fh:
#             fh = logging.FileHandler(path_abs, mode="a", encoding="utf-8")
#             fh.setLevel(logging.DEBUG)
#             fh.setFormatter(logging.Formatter(
#                 '%(asctime)s:%(levelname)s:%(message)s',
#                 datefmt='%m/%d/%Y %I:%M:%S %p'))
#             logger.addHandler(fh)
#
#         # console handler for dev
#         if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
#             ch = logging.StreamHandler()
#             ch.setLevel(logging.DEBUG)
#             ch.setFormatter(logging.Formatter('%(levelname)s:%(message)s'))
#             logger.addHandler(ch)
#
#         return logger
