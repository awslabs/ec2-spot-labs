#!/bin/sh

# How to test:
#  NAMESPACE=default POD_NAME=kubesh-3976960141-b9b9t ./this_script

# Set VERBOSE=1 to get more output
VERBOSE=${VERBOSE:-0}
function verbose () {
  [[ ${VERBOSE} -eq 1 ]] && return 0 || return 1
}

echo 'This script polls the "EC2 Spot Instance Termination Notices" endpoint to gracefully stop and then reschedule all the pods running on this Kubernetes node, up to 2 minutes before the EC2 Spot Instance backing this node is terminated.'
echo 'See https://aws.amazon.com/blogs/aws/new-ec2-spot-instance-termination-notices/ for more information.'

if [ "${NAMESPACE}" == "" ]; then
  echo '[ERROR] Environment variable `NAMESPACE` has no value set. You must set it via PodSpec like described in http://stackoverflow.com/a/34418819' 1>&2
  exit 1
fi

if [ "${POD_NAME}" == "" ]; then
  echo '[ERROR] Environment variable `POD_NAME` has no value set. You must set it via PodSpec like described in http://stackoverflow.com/a/34418819' 1>&2
  exit 1
fi

NODE_NAME=$(kubectl --namespace ${NAMESPACE} get pod ${POD_NAME} --output jsonpath="{.spec.nodeName}")

if [ "${NODE_NAME}" == "" ]; then
  echo "[ERROR] Unable to fetch the name of the node running the pod \"${POD_NAME}\" in the namespace \"${NAMESPACE}\". It might have problems initiating. Check logs for the pod using kubectl logs <podname> " 1>&2
  exit 1
fi

# Gather some information
AZ_URL=${AZ_URL:-http://169.254.169.254/latest/meta-data/placement/availability-zone}
AZ=$(curl -s ${AZ_URL})
INSTANCE_ID_URL=${INSTANCE_ID_URL:-http://169.254.169.254/latest/meta-data/instance-id}
INSTANCE_ID=$(curl -s ${INSTANCE_ID_URL})
if [ -z $CLUSTER ]; then
  echo "[WARNING] Environment variable CLUSTER has no name set. You can set this to get it reported in the Slack message." 1>&2
else
  CLUSTER_INFO=" (${CLUSTER})"
fi

echo "\`kubectl drain ${NODE_NAME}\` will be executed once a termination notice is made."

POLL_INTERVAL=${POLL_INTERVAL:-5}

NOTICE_URL=${NOTICE_URL:-http://169.254.169.254/latest/meta-data/spot/termination-time}

echo "Polling ${NOTICE_URL} every ${POLL_INTERVAL} second(s)"

# To whom it may concern: http://superuser.com/questions/590099/can-i-make-curl-fail-with-an-exitcode-different-than-0-if-the-http-status-code-i
while http_status=$(curl -o /dev/null -w '%{http_code}' -sL ${NOTICE_URL}); [ ${http_status} -ne 200 ]; do
  verbose && echo $(date): ${http_status}
  sleep ${POLL_INTERVAL}
done

echo $(date): ${http_status}
MESSAGE="Spot Termination${CLUSTER_INFO}: ${NODE_NAME}, Instance: ${INSTANCE_ID}, AZ: ${AZ}"

# Drain the node.
# https://kubernetes.io/docs/tasks/administer-cluster/safely-drain-node/#use-kubectl-drain-to-remove-a-node-from-service
kubectl drain ${NODE_NAME} --force --ignore-daemonsets

# Sleep for 200 seconds to prevent this script from looping.
# The instance should be terminated by the end of the sleep.
sleep 200
