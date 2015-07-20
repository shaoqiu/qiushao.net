android应用安装流程
------
**create time: 2015-07-17; update time: 2015-07-20**

---------------------------------------------------------------

android 应用的安装方式可以分为两种：有界面安装和静默安装。有界面安装是通过PackageInstaller 应用去安装的。这种安装形式可以让用户看到应用需要的权限，用户可以禁用相应的权限。静默安装是通过调用pm命令来安装的。本文主要介绍一下通过 PackageInstaller 安装应用的流程。

### 1. 发送安装请求给 PackageInstaller
我们通过 USB，或者网络下载应用后，都是通过 Intent 去调用 PackageInstaller 去安装的：
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

`pm` 即 PackageManager，这是一个抽象类。通过查看`ContextImpl.getPackageManager()`方法，发现它的真实类型为`ApplicationPackageManager`。`ApplicationPackageManager.installPackageWithVerificationAndEncryption`中只是调用了`installCommon`来干活而已。`installCommon`也只是调用了`ApplicationPackageManager.mPM.installPackage()`方法来干活。而`mPM`是在`ApplicationPackageManager`的构造函数中初始化的：
```java
ApplicationPackageManager(ContextImpl context, IPackageManager pm) {
        mContext = context;
        mPM = pm;
    }
```
我们回到`ContextImpl.getPackageManager()`中，发现`pm = ActivityThread.getPackageManager()`。跟进去：
```java
    public static IPackageManager getPackageManager() {
        if (sPackageManager != null) {
            //Slog.v("PackageManager", "returning cur default = " + sPackageManager);
            return sPackageManager;
        }
        IBinder b = ServiceManager.getService("package");
        //Slog.v("PackageManager", "default service binder = " + b);
        sPackageManager = IPackageManager.Stub.asInterface(b);
        //Slog.v("PackageManager", "default service = " + sPackageManager);
        return sPackageManager;
    }
```
`ServiceManager.getService("package");` 获取的其实就是`PackageManagerService`服务。我们可以查看`PackageManagerService.main()`：
```java
    public static final PackageManagerService main(Context context, Installer installer,
            boolean factoryTest, boolean onlyCore) {
        PackageManagerService m = new PackageManagerService(context, installer,
                factoryTest, onlyCore);
        ServiceManager.addService("package", m);
        return m;
    }
```
`PackageManagerService`是在系统启动时由`SystemServer`进程启动的，`SystemServer`又是由`Zygote`启动的。
WTFC，绕来绕去，绕了这么一大个圈。
好了，下面开始真正的干活了。

### 2. `PackageManagerService`安装应用过程
根据前面的分析，最终是调用了`PackageManagerService.installPackage()`来安装应用的。下面我们就转到`PackageManagerService`中分析。`installPackage`只是调用了`installPackageAsUser`来干活。下面来看`installPackageAsUser`的代码：
```java
    public void installPackageAsUser(String originPath, IPackageInstallObserver2 observer,
            int installFlags, String installerPackageName, VerificationParams verificationParams,
            String packageAbiOverride, int userId) {
        //开始作了一些权限的检查，忽略这些代码
        ......

	//判断是否从 adb 中安装APK，
        if ((callingUid == Process.SHELL_UID) || (callingUid == Process.ROOT_UID)) {
            installFlags |= PackageManager.INSTALL_FROM_ADB;
        } else {
        //这个例子中为否，会跑到这个分支，移除下面这两个标志位
            installFlags &= ~PackageManager.INSTALL_FROM_ADB;
            installFlags &= ~PackageManager.INSTALL_ALL_USERS;
        }

        UserHandle user;
        if ((installFlags & PackageManager.INSTALL_ALL_USERS) != 0) {
            user = UserHandle.ALL;
        } else {
            user = new UserHandle(userId);
        }

        verificationParams.setInstallerUid(callingUid);

        final File originFile = new File(originPath);
        final OriginInfo origin = OriginInfo.fromUntrustedFile(originFile);

        final Message msg = mHandler.obtainMessage(INIT_COPY);
        msg.obj = new InstallParams(origin, observer, installFlags,
                installerPackageName, verificationParams, user, packageAbiOverride);
        mHandler.sendMessage(msg);
    }
```
这个方法只是作了些安装权限的检查，初始化一些安装参数，最后把安装所需要的各种参数打包成`InstallParams`对象，我们可以把它当作一个安装任务。将其附加在一个`INIT_COPY`消息对象中，然后把这个消息发送出去。转到`mHandler.handleMessage`，这个方法调用了`doHandleMessage`来干活，截取我们感兴趣的部分来分析：
```java
                case INIT_COPY: {
	            //InstallParams 继承，并实现了HandlerParams抽象类
                    HandlerParams params = (HandlerParams) msg.obj;
                    int idx = mPendingInstalls.size();
                    if (DEBUG_INSTALL) Slog.i(TAG, "init_copy idx=" + idx + ": " + params);
                    // If a bind was already initiated we dont really
                    // need to do anything. The pending install
                    // will be processed later on.
                    if (!mBound) {
                        // If this is the only one pending we might
                        // have to bind to the service again.
                        if (!connectToService()) {
                            Slog.e(TAG, "Failed to bind to media container service");
                            params.serviceError();
                            return;
                        } else {
                            // Once we bind to the service, the first
                            // pending request will be processed.
                            mPendingInstalls.add(idx, params);
                        }
                    } else {
                        mPendingInstalls.add(idx, params);
                        // Already bound to the service. Just make
                        // sure we trigger off processing the first request.
                        if (idx == 0) {
                            mHandler.sendEmptyMessage(MCS_BOUND);
                        }
                    }
                    break;
                }
```
`mPendingInstalls`定义为:`new ArrayList<HandlerParams>();`，用来保存安装任务队列。首先绑定服务`connectToService`。这个方法绑定了`com.android.defcontainer.DefaultContainerService`服务，绑定成功时会调用：
```java
        public void onServiceConnected(ComponentName name, IBinder service) {
            if (DEBUG_SD_INSTALL) Log.i(TAG, "onServiceConnected");
            IMediaContainerService imcs =
                IMediaContainerService.Stub.asInterface(service);
            mHandler.sendMessage(mHandler.obtainMessage(MCS_BOUND, imcs));
        }
```
获取服务接口，并将其作为一个消息参数，发送`MCS_BOUND`消息。回到`doHandleMessage`，绑定服务后将安装任务添加到队列：`mPendingInstalls.add(idx, params)`。下面我们转移到`MCS_BOUND`消息处理分支：
```java
                case MCS_BOUND: {
                        .....
                        mContainerService = (IMediaContainerService) msg.obj;
                        ......
                    } else if (mPendingInstalls.size() > 0) {
                        HandlerParams params = mPendingInstalls.get(0);
                        if (params != null) {
                            if (params.startCopy()) {
                                // Delete pending install
                                if (mPendingInstalls.size() > 0) {
                                    mPendingInstalls.remove(0);
                                }
                                if (mPendingInstalls.size() == 0) {
                                    if (mBound) {
                                        removeMessages(MCS_UNBIND);
                                        Message ubmsg = obtainMessage(MCS_UNBIND);
                                        sendMessageDelayed(ubmsg, 10000);
                                    }
                                } else {
                                    mHandler.sendEmptyMessage(MCS_BOUND);
                                }
                            }
                        }
                        ......
```
取出安装任务队列头的任务，执行其`startCopy()`方法。执行完后，将该任务从任务队列中移除。如果任务队列为空则发送一个`MCS_UNBIND`消息，否则发送一个`MCS_BOUND`消息。安装任务就是通过这种消息机制依次安装，直到执行完所有的任务。`HandlerParams.startCopy()`又做了什么呢：
```java
        final boolean startCopy() {
            boolean res;
            try {
                if (++mRetries > MAX_RETRIES) {
                    mHandler.sendEmptyMessage(MCS_GIVE_UP);
                    handleServiceError();
                    return false;
                } else {
                    handleStartCopy();
                    res = true;
                }
            } catch (RemoteException e) {
                mHandler.sendEmptyMessage(MCS_RECONNECT);
                res = false;
            }
            handleReturnCode();
            return res;
        }
```
主要就是调用了`handleStartCopy()`和`handleReturnCode()`来复制和处理结果而已。下面转到`InstallParams.handleStartCopy()`：
```java
            //检查安装位置，剩余空间
            ......
            final InstallArgs args = createInstallArgs(this);
            mArgs = args;
            //验证安装信息
            ......
            ret = args.copyApk(mContainerService, true);
            mRet = ret; 
```
在此只关注关键代码，那些检查，校验操作就忽略了。调用`createInstallArgs`创建了一个`InstallArgs `：
```java
    private InstallArgs createInstallArgs(InstallParams params) {
        if (installOnSd(params.installFlags) || params.isForwardLocked()) {
           return new AsecInstallArgs(params);
        } else {
             return new FileInstallArgs(params);
        }
    }
```
`AsecInstallArgs`表示安装到SD卡，`FileInstallArgs`表示安装到系统内部存储（EMMC）。这里我们假设安装到内部存储。下面转到`FileInstallArgs.copyApk`：
```java

```

未完待续