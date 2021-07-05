"""
This file contains one class - SnapshotOps wich holds
operations on the enable, disable the features.uss option,
check for snapd process.
"""
from common.ops.abstract_ops import AbstractOps


class SnapshotOps(AbstractOps):
    """
    SnapshotOps class provides APIs to enable, disable
    the features.uss option, check for snapd process.
    """

    def enable_uss(self, volname: str, node: str,
                   excep: bool = True) -> dict:
        """
        Enables uss on the specified volume

        Args:
            volname (str): volume name
            node (str): Node on which cmd has to be executed.
        Optional:
            excep (bool): exception flag to bypass the exception if the
                          enable uss command fails. If set to False
                          the exception is bypassed and value from remote
                          executioner is returned. Defaults to True

        Returns:
            ret: A dictionary consisting
                - Flag : Flag to check if connection failed
                - msg : message
                - error_msg: error message
                - error_code: error code returned
                - cmd : command that got executed
                - node : node on which the command got executed
        """
        cmd = f"gluster volume set {volname} features.uss enable --mode=script"
        ret = self.execute_abstract_op_node(cmd, node, excep)
        return ret

    def disable_uss(self, volname: str, node: str,
                    excep: bool = True) -> dict:
        """
        Disable uss on the specified volume

        Args:
            volname (str): volume name
            node (str): Node on which cmd has to be executed.
        Optional:
            excep (bool): exception flag to bypass the exception if the
                          disable uss command fails. If set to False
                          the exception is bypassed and value from remote
                          executioner is returned. Defaults to True

        Returns:
            ret: A dictionary consisting
                - Flag : Flag to check if connection failed
                - msg : message
                - error_msg: error message
                - error_code: error code returned
                - cmd : command that got executed
                - node : node on which the command got executed
        """
        cmd = (f"gluster volume set {volname} features.uss disable"
               " --mode=script")
        ret = self.execute_abstract_op_node(cmd, node, excep)
        return ret

    def is_uss_enabled(self, volname: str, node: str) -> bool:
        """
        Check if uss is Enabled on the specified volume

        Args:
            volname (str): volume name
            node (str): Node on which cmd has to be executed.

        Returns:
            bool : True if successfully enabled uss on the volume.
                   False otherwise.
        """
        option_dict = self.get_volume_options(volname, "uss", node, False)
        if not option_dict:
            self.logger.error(f"USS is not set on the volume {volname}")
            return False

        if ('features.uss' in option_dict
                and option_dict['features.uss'] == 'enable'):
            return True

        return False

    def is_uss_disabled(self, volname: str, node: str) -> bool:
        """
        Check if uss is Disabled on the specified volume

        Args:
            volname (str): volume name
            node (str): Node on which cmd has to be executed.

        Returns:
            bool : True if successfully enabled uss on the volume.
                   False otherwise.
        """
        option_dict = self.get_volume_options(volname, "uss", node, False)
        if not option_dict:
            self.logger.error(f"USS is not set on the volume {volname}")
            return False

        if ('features.uss' in option_dict
                and option_dict['features.uss'] == 'disable'):
            return True

        return False

    def is_snapd_running(self, volname: str, node: str) -> bool:
        """
        Checks if snapd is running on the given node

        Args:
            volname (str): volume name
            node (str): Node on which cmd has to be executed.

        Returns:
            bool: True on success, False otherwise
        """
        vol_status = self.get_volume_status(volname, node)

        if vol_status is None:
            self.logger.error("Failed to get volume status in "
                              "is_snapd_running()")
            return False

        is_enabled = False
        online_status = True
        if 'node' in vol_status[volname]:
            for brick in vol_status[volname]['node']:
                if (brick['hostname'] == "Snapshot Daemon"
                        and brick['path'] == node):
                    is_enabled = True
                    if brick['status'] != '1':
                        online_status = False
                        break

        if not is_enabled:
            self.logger.error("Snapshot Daemon is not enabled for "
                              f"volume {volname}")
            return False
        if not online_status:
            self.logger.error("Snapshot Daemon is not running on node"
                              f" {node}")
            return False
        return True

    def snap_create(self, volname: str, snapname: str, node: str,
                    timestamp: bool = False, description: str = None,
                    force: bool = False, excep: bool = True) -> dict:
        """
        Function for snapshot creation.

        Args:
            volname (str): Name of the volume for which snap is
            is to be created.
            snapname (str): Name of the snapshot.
            node (str): Node wherein this command is to be run.

        Optional:
            timestamp (bool): Whether snap name should contain
            the timestamp or not. Default value being False.
            description (str): Description for snap creation.
            Default value is None.
            force (bool): Whether to create snap by force or not.
            By default it is False.
            excep (bool): Whether to handle exception or not.

        Returns:
            ret: A dictionary consisting
                - Flag : Flag to check if connection failed
                - msg : message
                - error_msg: error message
                - error_code: error code returned
                - cmd : command that got executed
                - node : node on which the command got executed
        """
        if description is not None:
            description = (f"description {description}")
        else:
            description = ''

        tstamp = ''
        if not timestamp:
            tstamp = "no-timestamp"

        frce = ''
        if force:
            frce = 'force'

        cmd = (f"gluster snapshot create {snapname} {volname}"
               f" {tstamp} {description} {frce} --mode=script --xml")

        return self.execute_abstract_op_node(cmd, node, excep)

    def snap_clone(self, snapname: str, clonename: str, node: str,
                   excep: bool = True) -> dict:
        """
        Method to clone a snapshot

        Args:
            snapname (str): Name of the snapshot.
            clonename (str): name of the clone.
            node (str): IP address of the node wherein the command
            is to be executed.

        Optional:
            excep (bool): Flag to control exception handling by the
            abstract ops. If True, the exception is handled, or else
            it isn't.

        Returns:
            ret: A dictionary consisting
                - Flag : Flag to check if connection failed
                - msg : message
                - error_msg: error message
                - error_code: error code returned
                - cmd : command that got executed
                - node : node on which the command got executed
        """
        cmd = (f"gluster snapshot clone {clonename} {snapname} --mode=script"
               " --xml")
        return self.execute_abstract_op_node(cmd, node, excep)

    def snap_restore(self, snapname: str, node: str,
                     excep: bool = True) -> bool:
        """
        Method to restore the snapshot.

        Args:
            snapname (str): Name of the snapshot
            node (str): Node wherien the command is to be executed.

        Optional:
            excep (bool): Flag to control exception handling by the
            abstract ops. If True, the exception is handled, or else
            it isn't.

        Returns:
            ret: A dictionary consisting
                - Flag : Flag to check if connection failed
                - msg : message
                - error_msg: error message
                - error_code: error code returned
                - cmd : command that got executed
                - node : node on which the command got executed
        """
        cmd = (f"gluster snapshot restore {snapname} --mode=script --xml")
        return self.execute_abstract_op_node(cmd, node, excep)

    def snap_restore_complete(self, volname: str, snapname: str,
                              node: str, excep: bool = True) -> bool:
        """
        Method restore the snapshot and that is done when volume is stopped.
        Post snap restore, the volume is started again.

        Args:
            volname (str): Name of the volume.
            snpaname (str): name of the snapshot.
            node (str): node wherien the command is to be executed.

        Optional:
            excep (bool): Flag to control exception handling by the
            abstract ops. If True, the exception is handled, or else
            it isn't.

        Returns:
            bool: True if restore is a success or False.
        """
        # Stop the volume.
        self.volume_stop(volname, node, force=True)

        ret = self.snap_restore(volname, snapname, node, excep)

        if ret['msg']['opRet'] != 0:
            return False

         # Start the volume
        self.volume_start(volname, node, force=True)

        return True

    def snap_status(self, node, snapname: str = None, volname: str = None,
                    excep: bool = True) -> dict:
        """
        Method for obtaining the snapshot status.

        Args:
            node (str): node wherein the command is to be executed.

        Optional:
            snapname (str): The name of the snapshot
            volname (str): The name of the volume.
            excep (bool): Flag to control exception handling by the
            abstract ops. If True, the exception is handled, or else
            it isn't.

        Returns:
            ret: A dictionary consisting
                - Flag : Flag to check if connection failed
                - msg : message
                - error_msg: error message
                - error_code: error code returned
                - cmd : command that got executed
                - node : node on which the command got executed
        """
        if snapname is None and volname is None:
            raise Exception("Provide either snapname or volume name.")
        elif snapname is not None:
            cmd = (f"gluster snapshot status {snapname} --mode=script --xml")
        elif volname is not None:
            cmd = (f"gluster snapshot status volume {volname} --mode=script"
                   " --xml")
        return self.execute_abstract_op_node(cmd, node, excep)

    def get_snap_status(self, node: str) -> list:
        """
        Method to get and parse the snapshot status.

        Args:
            node (str): node wherein the command will be run.

        Returns:
            List of snapshot statuses.
        """
        cmd = "gluster vol snapshot status --xml --mode=script"
        ret = self.execute_abstract_op_node(cmd, node)

        snap_status_list = []
        # TODO parsing logic for snap status.

        return snap_status_list

    def get_snap_status_by_snapname(self, snapname: str, node: str) -> dict:
        """
        Method to get a snap status for a specific snapshot.

        Args:
            snapname (str): name of the snapshot
            node (str): node wherein the command is to be executed.

        Returns:
            Dictionary of the snap status for the said snapshot or Nonetype
            object.
        """
        snap_status_list = self.get_snap_status(node)

        for snap_status in snap_status_list:
            if "name" in snap_status:
                if snap_status["name"] == snapname:
                    return snap_status
        return None

    def get_snap_status_by_volname(self, volname: str, node: str) -> list:
        """
        Method to get the snap status for given volume

        Args:
            volname (str): name of the volume.
            node (str): node wherein the command is to be executed.

        Returns:
            List of snapshot status dictionaries.
        """
        snap_status_list = self.get_snap_status(node)

        vol_snap_status_list = []

        # TODO parsing logic to be added.
        return vol_snap_status_list

    def snap_info(self, node: str, snapname: str = None, volname: str = None,
                  excep: bool = True) -> dict:
        """
        Method to obtain the snap info.

        Args:
            node (str): Node wherein the command is run.

        Optional:
            snapname (str): name of the snapshot
            volname (str): name of the volume.
            except (bool): Flag to control exception handling by the
            abstract ops. If True, the exception is handled, or else
            it isn't.

        Returns:
            ret: A dictionary consisting
                - Flag : Flag to check if connection failed
                - msg : message
                - error_msg: error message
                - error_code: error code returned
                - cmd : command that got executed
                - node : node on which the command got executed
        """
        if snapname is None and volname is None:
            raise Exception("Provide either snapname or volname.")
        elif snapname is not None:
            cmd = (f"gluster snapshot info {snapname} --mode=script --xml")
        elif volname is not None:
            cmd = (
                f"gluster snapshot info volume {volname} --xml --mode=script")
        return self.execute_abstract_op_node(cmd, node, excep)

    def get_snap_info(self, node: str, excep: bool = True) -> dict:
        """
        Method to obtain the snap status command output when run in a node

        Args:
            node (str): Node wherein the command is to be run.

        Optional:
            excep (bool): Flag to control exception handling by the
            abstract ops. If True, the exception is handled, or else
            it isn't.

        Returns:
            ret: A dictionary consisting
                - Flag : Flag to check if connection failed
                - msg : message
                - error_msg: error message
                - error_code: error code returned
                - cmd : command that got executed
                - node : node on which the command got executed
        """
        cmd = "gluster snapshot info --xml --mode=script"
        ret = self.execute_abstract_op_node(cmd, node, excep)

        if not excep and ret['msg']['opRet'] != '0':
            return None

        snap_info_list = []
        # TODO add snap info parsing here.
        return snap_info_list

    def get_snap_info_by_snapname(self, snapname: str, node: str) -> dict:
        """
        Method to obtain the snap info specific to a snapname.

        Args:
            snapname (str): name of the snapshot.
            node (str): the node wherein the command has to be run.

        Returns:
            dictionary of the snap status or Nonetype object.
        """
        snap_info_list = self.get_snap_info(node)
        for snap_info in snap_info_list:
            if "name" in snap_info:
                if snap_info["name"] == snapname:
                    return snap_info
        return None

    def get_snap_info_by_volname(self, volname: str, node: str) -> dict:
        """
        Method to obtain the snap info specific to volume

        Args:
            volname (str): name of the volume.
            node (str): the node wherein the command has to be run.

        Returns:
            dictionary of the snap status or Nonetype object.
        """
        snap_info_list = self.get_snap_info(node)
        # TODO add logic for volume level parsing.
        return None

    def snap_list(self, node: str, excep: bool = True) -> dict:
        """
        Method to list the snapshots in a node.

        Args:
            node (str): Node wherein the command will be executed.

        Optional:
            except (bool): Flag to control exception handling by the
            abstract ops. If True, the exception is handled, or else
            it isn't.

        Returns:
            ret: A dictionary consisting
                - Flag : Flag to check if connection failed
                - msg : message
                - error_msg: error message
                - error_code: error code returned
                - cmd : command that got executed
                - node : node on which the command got executed
        """
        cmd = "gluster snapshot list --mode=script --xml"
        return self.execute_abstract_op_node(cmd, node, excep)

    def get_snap_list(self, node: str, volname: str = None,
                      excep: bool = True) -> list:
        if volname is None:
            cmd = "gluster snapshot list --xml --mode=script"
        else:
            cmd = (f"gluster snapshot list {volname} --xml"
                   " --mode=script")

        ret = self.execute_abstract_op_node(cmd, node, excep)
        # TODO add the parsing logic in here.

        return ret

    def snap_delete(self, snapname: str, node: str,
                    excep: bool = True) -> dict:
        """
        Method to delete snapshot.

        Args:
            snapname (str): name of the snapshot.
            node (str): Node wherein the command is to be executed.

        Optional:
            excep (bool): Flag to control exception handling by the
            abstract ops. If True, the exception is handled, or else
            it isn't.

        Returns:
            ret: A dictionary consisting
                - Flag : Flag to check if connection failed
                - msg : message
                - error_msg: error message
                - error_code: error code returned
                - cmd : command that got executed
                - node : node on which the command got executed
        """
        cmd = (f"gluster snapshot delete {snapname} --xml --mode=script")
        return self.execute_abstract_op_node(cmd, node, excep)

    def snap_delete_by_volumename(self, volname: str, node: str,
                                  excep: bool = True) -> dict:
        """
        Method to delete a snapshot by volumename.

        Args:
            volname (str): name of the volume.
            node (str): Node whereint he command is to be executed.

        Optional:
            excep (bool): Flag to control exception handling by the
            abstract ops. If True, the exception is handled, or else it
            isn't.

        Returns:
            ret: A dictionary consisting
                - Flag : Flag to check if connection failed
                - msg : message
                - error_msg: error message
                - error_code: error code returned
                - cmd : command that got executed
                - node : node on which the command got executed
        """
        cmd = (f"gluster snapshot volume {volname} --xml --mode=script")
        return self.execute_abstract_op_node(cmd, node, excep)

    def snap_delete_all(self, node: str, excep: bool = True) -> dict:
        """
        Method to delete all snapshots in the cluster.

        Args:
            node (str): Node wherein the command is to be run. This node
            has to be part of the cluster wherein the snapshots are being
            deleted.

        Optional:
            excep (bool): Flag to control exception handling by the
            abstract ops. If True, the exception is handled, or else it
            isn't.

        Returns:
            ret: A dictionary consisting
                - Flag : Flag to check if connection failed
                - msg : message
                - error_msg: error message
                - error_code: error code returned
                - cmd : command that got executed
                - node : node on which the command got executed
        """
        cmd = "gluster snapshot delete all --mode=script --xml"
        return self.execute_abstract_op_node(cmd, node, excep)
