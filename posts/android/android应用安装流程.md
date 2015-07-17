android应用安装流程
------
**create time: 2015-07-17; update time: 2015-07-17**

---------------------------------------------------------------

android 应用的安装方式可以分为两种：有界面安装和静默安装。有界面安装是通过PackageInstaller 应用去安装的。这种安装形式可以让用户看到应用需要的权限，用户可以禁用相应的权限。静默安装是通过调用pm命令来安装的。本文主要介绍一下通过 PackageInstaller 安装应用的流程。

### 1. 发送安装请求给 PackageInstaller
我们通过 USB，或者网络下载应用后，都是通过 Intent 调用 PackageInstaller 去安装的：
```java
String fileName = "/mnt/usb/sda4/test.apk";
Intent intent = new Intent(Intent.ACTION_VIEW);
intent.setDataAndType(Uri.fromFile(new File(fileName)), "application/vnd.android.package-archive");
startActivity(intent);
```

PackageInstaller 解析待安装在APK，检查权限，然后由用户确定是否要安装。这个过程的代码不是重点，在此就省略了。其他源码在`ANDROID_ROOT/packages/apps/PackageInstaller`中。用户确认安装后，最后调用了：
```java
pm = getPackageManager();
.......
pm.installPackageWithVerificationAndEncryption(mPackageURI, observer, installFlags, installerPackageName, verificationParams, null);
```

`pm` 即 PackageManager，这是一个抽象类。通过查看`ContextImpl.getPackageManager()`方法，发现它的真实类型为`ApplicationPackageManager`。