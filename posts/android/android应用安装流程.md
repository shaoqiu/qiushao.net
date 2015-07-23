android应用安装流程
------
**create time: 2015-07-17; update time: 2015-07-23**

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
                ......
                //创建一个临时文件夹：/data/app/vmdlxxx.tmp,“xxx”为一个随机数
                final File tempDir = mInstallerService.allocateInternalStageDirLegacy();
                codeFile = tempDir;
                resourceFile = tempDir;
                ......

                //这个回调接口会由imcs 服务回调
                final IParcelFileDescriptorFactory target = new IParcelFileDescriptorFactory.Stub() {
                @Override
                public ParcelFileDescriptor open(String name, int mode) throws RemoteException {
                    if (!FileUtils.isValidExtFilename(name)) {
                        throw new IllegalArgumentException("Invalid filename: " + name);
                    }
                    try {
                        final File file = new File(codeFile, name);
                        final FileDescriptor fd = Os.open(file.getAbsolutePath(),
                                O_RDWR | O_CREAT, 0644);
                        Os.chmod(file.getAbsolutePath(), 0644);
                        return new ParcelFileDescriptor(fd);
                    } catch (ErrnoException e) {
                        throw new RemoteException("Failed to open: " + e.getMessage());
                    }
                }
            };

            int ret = PackageManager.INSTALL_SUCCEEDED;
            //通过 imcs 服务，把APK文件复制到 /data/app/vmdlxxx.tmp 目录下
            //imcs 服务为 DefaultContainerService.java 
            //搞了这么复杂就是为了把原始的APK复制到 /data/app/vmdlxxx.tmp/base.apk
            ret = imcs.copyPackage(origin.file.getAbsolutePath(), target);
            if (ret != PackageManager.INSTALL_SUCCEEDED) {
                Slog.e(TAG, "Failed to copy package");
                return ret;
            }    
            
            //提取APK中的SO动态库文件到/data/app/vmdlxxx.tmp/lib目录
            final File libraryRoot = new File(codeFile, LIB_DIR_NAME);
            NativeLibraryHelper.Handle handle = null;
            try {
                handle = NativeLibraryHelper.Handle.create(codeFile);
                ret = NativeLibraryHelper.copyNativeBinariesWithOverride(handle, libraryRoot,
                        abiOverride);
            } catch (IOException e) {
                Slog.e(TAG, "Copying native libraries failed", e);
                ret = PackageManager.INSTALL_FAILED_INTERNAL_ERROR;
            } finally {
                IoUtils.closeQuietly(handle);
            }
            return ret;
```
不知道是不是我想的太简单了，我觉得不就是创建个临时目录，复制个文件，解压个文件而已吗，为什么要搞得这么复杂？又是远程服务调用，又是native调用的。
至此，复制APK的步骤已经完成了，成果就是在 `data/app`目录下新建了一个临时目录`vmdlxxx.tmp`，将原始的APK文件复制到这个临时目录命名为`base.apk`，并将APK中的动态库文件提取到这个`/data/app/vmdlxxx.tmp/lib`目录。这些操作一切正常的话，就返回上层调用，继续安装步骤。下面流程回到`HandlerParams.startCopy()`中，接下来调用了`InstallParams.handleReturnCode();`根据复制APK的结果进行处理，这个方法只是调用了`processPendingInstall`来干活而已：
```java
    private void processPendingInstall(final InstallArgs args, final int currentStatus) {
        // Queue up an async operation since the package installation may take a little while.
        mHandler.post(new Runnable() {
            public void run() {
            ......
            if (res.returnCode == PackageManager.INSTALL_SUCCEEDED) {
                    args.doPreInstall(res.returnCode);
                    synchronized (mInstallLock) {
                        installPackageLI(args, res);
                    }
                    args.doPostInstall(res.returnCode, res.uid);
            }
            //接下来是一些备份工作，在此我们不关注
            ......
            Message msg = mHandler.obtainMessage(POST_INSTALL, token, 0);
            mHandler.sendMessage(msg);                
```
这个方法调用了`FileInstallArgs.doPreInstall`做些准备工作， `installPackageLI`开始安装，`FileInstallArgs.doPostInstall`扫尾工作。最后再发了一个`POST_INSTALL`消息出来。`doPostInstall`只是清理上一步骤创建的临时目录而已，不需要过多分析，下面我们来分析`installPackageLI`：
```java
        //提取安装参数
        ......
        //解析APK文件
        final int parseFlags = mDefParseFlags | PackageParser.PARSE_CHATTY
                | (forwardLocked ? PackageParser.PARSE_FORWARD_LOCK : 0)
                | (onSd ? PackageParser.PARSE_ON_SDCARD : 0);
        PackageParser pp = new PackageParser();
        pp.setSeparateProcesses(mSeparateProcesses);
        pp.setDisplayMetrics(mMetrics);

        final PackageParser.Package pkg;
        try {
            pkg = pp.parsePackage(tmpPackageFile, parseFlags);
        } catch (PackageParserException e) {
            res.setError("Failed parse during installPackageLI", e);
            return;
        }
        //签名验证
        ......
        //APK是否安装过
        ......
        
        if (!args.doRename(res.returnCode, pkg, oldCodePath)) {
            res.setError(INSTALL_FAILED_INSUFFICIENT_STORAGE, "Failed rename");
            return;
        }

        if (replace) {
            replacePackageLI(pkg, parseFlags, scanFlags | SCAN_REPLACING, args.user,
                    installerPackageName, res);
        } else {
            installNewPackageLI(pkg, parseFlags, scanFlags | SCAN_DELETE_DATA_ON_FAILURES,
                    args.user, installerPackageName, res);
        }
        synchronized (mPackages) {
            final PackageSetting ps = mSettings.mPackages.get(pkgName);
            if (ps != null) {
                res.newUsers = ps.queryInstalledUsers(sUserManager.getUserIds(), true);
            }
        }
    }
```
首先使用`PackageParser.parsePackage`来解析APK文件，得到一个 `PackageParser.Package pkg`对象。解析APK，其实就是使用 XML 解析器去解析 `AndroidManifest.xml`文件而已。最终调用了`parseBaseApk(Resources res, XmlResourceParser parser, int flags, String[] outError)`方法来解析：
```java
    private Package parseBaseApk(Resources res, XmlResourceParser parser, int flags,
            String[] outError) throws XmlPullParserException, IOException {
        final boolean trustedOverlay = (flags & PARSE_TRUSTED_OVERLAY) != 0;
        ......
        while ((type = parser.next()) != XmlPullParser.END_DOCUMENT
                && (type != XmlPullParser.END_TAG || parser.getDepth() > outerDepth)) {
            if (type == XmlPullParser.END_TAG || type == XmlPullParser.TEXT) {
                continue;
            }

            String tagName = parser.getName();
            if (tagName.equals("application")) {
                if (foundApp) {
                    if (RIGID_PARSER) {
                        outError[0] = "<manifest> has more than one <application>";
                        mParseError = PackageManager.INSTALL_PARSE_FAILED_MANIFEST_MALFORMED;
                        return null;
                    } else {
                        Slog.w(TAG, "<manifest> has more than one <application>");
                        XmlUtils.skipCurrentTag(parser);
                        continue;
                    }
                }

                foundApp = true;
                if (!parseBaseApplication(pkg, res, parser, attrs, flags, outError)) {
                    return null;
                }
            } else if (tagName.equals("overlay")) {
                pkg.mTrustedOverlay = trustedOverlay;
                ......
            } else if (tagName.equals("key-sets")) {
                if (!parseKeySets(pkg, res, parser, attrs, outError)) {
                    return null;
                }
            } else if (tagName.equals("permission-group")) {
                if (parsePermissionGroup(pkg, flags, res, parser, attrs, outError) == null) {
                    return null;
                }
            } else if (tagName.equals("permission")) {
                if (parsePermission(pkg, res, parser, attrs, outError) == null) {
                    return null;
                }
            } else if (tagName.equals("permission-tree")) {
                if (parsePermissionTree(pkg, res, parser, attrs, outError) == null) {
                    return null;
                }
            } else if (tagName.equals("uses-permission")) {
                if (!parseUsesPermission(pkg, res, parser, attrs, outError)) {
                    return null;
                }
            } else if (tagName.equals("uses-configuration")) {
            .......
                
```
我们看到`application`标签，这个标签里面包含了`activity`，`service`，`provider`，`broacast`等标签。我们跟进`parseBaseApplication`函数里面，就会发现里面对这些标签进行了解析：
```java
        while ((type = parser.next()) != XmlPullParser.END_DOCUMENT
                && (type != XmlPullParser.END_TAG || parser.getDepth() > innerDepth)) {
            if (type == XmlPullParser.END_TAG || type == XmlPullParser.TEXT) {
                continue;
            }

            String tagName = parser.getName();
            if (tagName.equals("activity")) {
                Activity a = parseActivity(owner, res, parser, attrs, flags, outError, false,
                        owner.baseHardwareAccelerated);
                if (a == null) {
                    mParseError = PackageManager.INSTALL_PARSE_FAILED_MANIFEST_MALFORMED;
                    return false;
                }

                owner.activities.add(a);

            } else if (tagName.equals("receiver")) {
                Activity a = parseActivity(owner, res, parser, attrs, flags, outError, true, false);
                if (a == null) {
                    mParseError = PackageManager.INSTALL_PARSE_FAILED_MANIFEST_MALFORMED;
                    return false;
                }

                owner.receivers.add(a);

            } else if (tagName.equals("service")) {
                Service s = parseService(owner, res, parser, attrs, flags, outError);
                if (s == null) {
                    mParseError = PackageManager.INSTALL_PARSE_FAILED_MANIFEST_MALFORMED;
                    return false;
                }

                owner.services.add(s);

            } else if (tagName.equals("provider")) {
                Provider p = parseProvider(owner, res, parser, attrs, flags, outError);
                if (p == null) {
                    mParseError = PackageManager.INSTALL_PARSE_FAILED_MANIFEST_MALFORMED;
                    return false;
                }

                owner.providers.add(p);
                ......
```
最终将解析出来的`activity`， `service`等组件保存到`Package.activities`，`Package.services`等数组中。具体的解析细节我们就不过多关注了。我们返回到`installPackageLI`中，接下来进行签名信息的检验，判断APK是否安装过，这些过程我们就忽略了。然后调用了`args.doRename`将临时目录重命名为`包名-x`，其中`x >= 1`。最终调用了`installNewPackageLI`进一步安装：
```java
    private void installNewPackageLI(PackageParser.Package pkg,
            int parseFlags, int scanFlags, UserHandle user,
            String installerPackageName, PackageInstalledInfo res) {
            ......
            PackageParser.Package newPackage = scanPackageLI(pkg, parseFlags, scanFlags,
                    System.currentTimeMillis(), user);

            updateSettingsLI(newPackage, installerPackageName, null, null, res);
            ......
```
调用`scanPackageLI`干活，`scanPackageLI`又调用了`scanPackageDirtyLI`去真正的干活：
```java
    private PackageParser.Package scanPackageDirtyLI(PackageParser.Package pkg, int parseFlags,
            int scanFlags, long currentTime, UserHandle user) throws PackageManagerException {
        final File scanFile = new File(pkg.codePath);
        ......
        File destCodeFile = new File(pkg.applicationInfo.getCodePath());
        File destResourceFile = new File(pkg.applicationInfo.getResourcePath());
        ......
        dataPath = getDataPathForPackage(pkg.packageName, 0);
        ......
        //invoke installer to do the actual installation
        int ret = createDataDirsLI(pkgName, pkg.applicationInfo.uid,
                                           pkg.applicationInfo.seinfo);
        ......
        setNativeLibraryPaths(pkg);
        ......
        handle = NativeLibraryHelper.Handle.create(scanFile);
        ......
        copyRet = NativeLibraryHelper.copyNativeBinariesForSupportedAbi(handle,
                                nativeLibraryRoot, abiList, useIsaSpecificSubdirs);
        ......
        setNativeLibraryPaths(pkg);
        ......
        mInstaller.linkNativeLibraryDirectory(pkg.packageName, nativeLibPath, userId)
        ......

        // writer
        synchronized (mPackages) {
            // We don't expect installation to fail beyond this point

            // Add the new setting to mSettings
            mSettings.insertPackageSettingLPw(pkgSetting, pkg);
            // Add the new setting to mPackages
            mPackages.put(pkg.applicationInfo.packageName, pkg);
            ......
            int N = pkg.providers.size();
            StringBuilder r = null;
            int i;
            for (i=0; i<N; i++) {
                PackageParser.Provider p = pkg.providers.get(i);
                p.info.processName = fixProcessName(pkg.applicationInfo.processName,
                        p.info.processName, pkg.applicationInfo.uid);
                mProviders.addProvider(p);
            ......
            N = pkg.services.size();
            r = null;
            for (i=0; i<N; i++) {
                PackageParser.Service s = pkg.services.get(i);
                s.info.processName = fixProcessName(pkg.applicationInfo.processName,
                        s.info.processName, pkg.applicationInfo.uid);
                mServices.addService(s);
            ......
            N = pkg.activities.size();
            r = null;
            for (i=0; i<N; i++) {
                PackageParser.Activity a = pkg.activities.get(i);
                a.info.processName = fixProcessName(pkg.applicationInfo.processName,
                        a.info.processName, pkg.applicationInfo.uid);
                mActivities.addActivity(a, "activity");
            ......
            
```
这个方法做了很多工作，先创建 APK 的 data 目录，然后将APK的资源文件，动态库等文件提取到 data 目录，并做相应的配置。最后将在`AndroidManifest.xml`中收集到的四大组件及其他的信息增加到`PackageManagerService`的成员变量`mActivities`，`mServices`，`providers`，`mPermissionGroups`中。其实`PackageManagerService`在启动时会读`/data/system/package.xml`文件对上面这些成员变量进行初始化。当需要启动 Activity 等组件时，就会从这些成员变量中寻找相应的信息。下一步就是将新增APK的信息写入到`/data/system/package.xml`文件中：
```java
    private void updateSettingsLI(PackageParser.Package newPackage, String installerPackageName,
            int[] allUsers, boolean[] perUserInstalled,
            PackageInstalledInfo res) {
            ......
            synchronized (mPackages) {
            //write settings. the installStatus will be incomplete at this stage.
            //note that the new package setting would have already been
            //added to mPackages. It hasn't been persisted yet.
            mSettings.setInstallStatus(pkgName, PackageSettingBase.PKG_INSTALL_INCOMPLETE);
            mSettings.writeLPr();
        }
        ......
            mSettings.setInstallStatus(pkgName, PackageSettingBase.PKG_INSTALL_COMPLETE);
            mSettings.setInstallerPackageName(pkgName, installerPackageName);
            res.returnCode = PackageManager.INSTALL_SUCCEEDED;
            //to update install status
            mSettings.writeLPr();
            
```
主要是调用了`mSettings.writeLPr();`方法来保存数据：
```java
    void writeLPr() {
        ......
        try {
            FileOutputStream fstr = new FileOutputStream(mSettingsFilename);
            BufferedOutputStream str = new BufferedOutputStream(fstr);

            //XmlSerializer serializer = XmlUtils.serializerInstance();
            XmlSerializer serializer = new FastXmlSerializer();
            serializer.setOutput(str, "utf-8");
            serializer.startDocument(null, true);
```
`mSettingsFilename = "/data/system/package.xml"` ，就是使用`XmlSerializer`来生成`xml`文件而已。过程就不具体讲解了。不过我们注意到`mSettings.writeLPr()`被调用了两次。第一次调用前设置了`PackageSettingBase.PKG_INSTALL_INCOMPLETE`状态，说明APK还未安装完成，还不可用。第二次调用前设置了`PackageSettingBase.PKG_INSTALL_COMPLETE`状态，说明APk已经安装完成，可以使用了。这个状态标志在`writeLPr()`会读取，并作相应的处理：
```java
        if (pkg.installStatus == PackageSettingBase.PKG_INSTALL_INCOMPLETE) {
            serializer.attribute(null, "installStatus", "false");
        }
```

至此，一个应用的安装可以说是已经完成了。我们回到`processPendingInstall`方法中，接下来调用了`args.doPostInstall(res.returnCode, res.uid);`进行一些清理工作：
```java
        int doPostInstall(int status, int uid) {
            if (status != PackageManager.INSTALL_SUCCEEDED) {
                cleanUp();
            }
            return status;
        }
```
`cleanUp()`只是删除一些临时文件而已，不多作解析。`processPendingInstall`在最后发了一个`POST_INSTALL`消息出来。这样流程就转到`doHandleMessage`中了，我们看看`POST_INSTALL`消息处理分支：
```java
                case POST_INSTALL: {
                    if (DEBUG_INSTALL) Log.v(TAG, "Handling post-install for " + msg.arg1);
                    PostInstallData data = mRunningInstalls.get(msg.arg1);
                    mRunningInstalls.delete(msg.arg1);
                    ......
                    //发Intent.ACTION_PACKAGE_REMOVED广播
                    res.removedInfo.sendBroadcast(false, true, false);
                    ......
                    //发Intent.ACTION_PACKAGE_ADDED广播
                    sendPackageBroadcast(Intent.ACTION_PACKAGE_ADDED,
                                    res.pkg.applicationInfo.packageName,
                                    extras, null, null, firstUsers);
                    ......
                    //最后通知安装请求者，安装已经完成了
                    args.observer.onPackageInstalled(res.name, res.returnCode,
                                        res.returnMsg, extras);
```
至此，一个应用的所有安装流程已经走完了。系统继续查看安装任务队列，如果还有任务则执行下一个安装任务。

整个安装流程非常复杂，这里只是提取了一个主线来分析而已，还有很细枝末节的工作被忽略掉了。当遇到具体问题时，再详细跟踪分析细节问题就可以了。

应用已经安装完了，但系统是怎么启动一个应用的呢，下一往篇文章再具体分析。