#!/bin/bash
w=$3
c=$4
queuesize=`sudo /usr/sbin/rabbitmqctl list_queues -p $1 name messages | grep $2 | awk '{print $2}'`

if [ $queuesize -lt $w ]
then
	state=OK
fi

if [ $queuesize -lt $c -a $queuesize -gt $w ]
then
        state=WARNING
fi

if [ $queuesize -gt $c ]
then
        state=CRITICAL
fi

if [ -z $state ]
then
        state=CRITICAL
fi

echo "RABBITMQ $state - $queuesize Messages in Queue|messages=$queuesize;$3;$4;0;$queuesize"

