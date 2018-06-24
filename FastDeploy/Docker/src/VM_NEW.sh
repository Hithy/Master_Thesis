#!/bin/bash
INSTANCE=`date +%s%N`
VMDIR=./vms/$INSTANCE
SRCDIR=./img_test
VMIMAGE_SRC=$SRCDIR/new.qcow2
VMIMAGE_NEW=$VMDIR/image.qcow2
CONFIG_ISO=$VMDIR/config.iso

mkdir -p $VMDIR
cp $VMIMAGE_SRC $VMIMAGE_NEW

touch $VMDIR/meta-data

echo "instance-id: $INSTANCE" >> $VMDIR/meta-data
echo "local-hostname: test_$INSTANCE" >> $VMDIR/meta-data
echo "public-keys:" >> $VMDIR/meta-data
echo " - ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC87q6wBAjGAymVTJ8RvbjH9gn12P88D9kzwNEOTvenHAyHMUjWCwhSIQylRyAS+VraiGzNxx8iWHcfoMks4tR+U0OegHDkw2Uz6U6v1Kb+fvu9TnzQ0ZZP4yOO8jx73hyrNihosZLOQSAFKHOFdIO3cYPfB/ETJjIszgcSPlnV35pVJZ0Cc+JJT2waxwQIlIgVjiBayMp4UUNyDr3uxaMG2MmI/J3EuUft9EB3GdixD5PtdpJasT3iYQq5poYaA3gSwKx0zSiwpziGuVbkSdCmRCz/qC/Ohj1RlFd2kSRtZ4KFWNLSXs6jVzbBSKLi10aGbzFm2mCYvTfzcjC/8O/1 root@root2" >> $VMDIR/meta-data

genisoimage -o $CONFIG_ISO -V cidata -r -J $VMDIR/meta-data $SRCDIR/user-data
#genisoimage -o $CONFIG_ISO -V cidata -r -J $SRCDIR/meta-data $SRCDIR/user-data
rm -rf $VMDIR/meta-data


  #--graphics vnc,listen=0.0.0.0 --noautoconsole \

virt-install --virt-type kvm --name test_$INSTANCE --ram 512 \
  --disk $VMIMAGE_NEW,format=qcow2 \
  --disk path=$CONFIG_ISO,device=cdrom \
  --import \
  --network network=default \
  --noautoconsole \
  --os-type=linux --os-variant=ubuntutrusty
