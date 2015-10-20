SQLiteOpenHelper指定数据库路径
------
**create time: 2015-10-20; update time: 2015-10-20**


---------------------------------------------------------------

Android提供了创建和使用SQLite数据库的API：`SQLiteDatabase`，但通常我们不推荐直接使用SQLiteDatabase来打开数据库，而应该通过`SQLiteOpenHelper`来管理数据库的创建和版本更新。一般用法是定义一个类继承SQLiteOpenHelper，并实现两个抽象方法：onCreate(SQLiteDatabase db)和onUpgrade(SQLiteDatabase db,int oldVersion,int newVersion)来创建和跟新数据库，然后通过getWritableDatabase()方法获取SQLiteDatabase的可操作实例。

最近在开发[DBHelper](https://github.com/qiushao/DBHelper)的时候，同事提了个需求：可以指定数据库的目录，以便将数据库放在一个公共的目录供其他应用访问。本来我觉得这种需求应该是使用ContentProvider来实现的，所有应用都通过同一个ContentProvider接口去操作一个数据库，但是同事说，由于历史原因，旧的版本是直接将数据库放到一个公共的目录供所有应用操作的。如果要修改为ContentProvider的话，可能改动比较大，为了维护旧的版本，还是增加了指定数据库目录这个功能。

DBHelper 内部也是使用SQLiteOpenHelper来操作数据库的，但看了API之后发现居然没有提供指定数据库路径的接口。SQLiteOpenHelper 默认创建的数据库都是放在`/data/data/PACKAGE_NAME/databases`目录下的。于是百度，google之，发现也有很多人遇到了同样的需求，有的直接使用SQLiteDatabase来操作数据库，也有人提供了一种思路：重写`ContextWrapper.getDatabasePath()`方法。具体原理请看SQLiteOpenHelper源码：
```
try {
    if (DEBUG_STRICT_READONLY && !writable) {
        final String path = mContext.getDatabasePath(mName).getPath();
        db = SQLiteDatabase.openDatabase(path, mFactory,
                SQLiteDatabase.OPEN_READONLY, mErrorHandler);

    } else {
        db = mContext.openOrCreateDatabase(mName, mEnableWriteAheadLogging ?
                Context.MODE_ENABLE_WRITE_AHEAD_LOGGING : 0,
                mFactory, mErrorHandler);
    }
}
```
这是SQLiteOpenHelper打开数据库的相关代码，我们可以看到，如果是以只读方式打开数据库的话，是通过`mContext.getDatabasePath(mName).getPath();`方法来获取数据路径的。如果是以可写方式打开数据库的话，是通过`mContext.openOrCreateDatabase`方法来打开数据库的。所以只要我们重写了这两个方法就可以达到自定义数据库路径的目的了。具体实现参见[http://www.tuicool.com/articles/neEz2qr](http://www.tuicool.com/articles/neEz2qr)。

但是这两天比较空闲，去看了一下android源码中`ContextImpl`类的`getDatabasePath`和`openOrCreateDatabase`方法的具体实现，发现这两个方法最终都是调用了`private File validateFilePath(String name, boolean createDirectory)`这个私有方法去获取数据库的路径的。具体实现如下：
```
private File validateFilePath(String name, boolean createDirectory) {
    File dir;
    File f;

    if (name.charAt(0) == File.separatorChar) {
        String dirPath = name.substring(0, name.lastIndexOf(File.separatorChar));
        dir = new File(dirPath);
        name = name.substring(name.lastIndexOf(File.separatorChar));
        f = new File(dir, name);
    } else {
        dir = getDatabasesDir();
        f = makeFilename(dir, name);
    }
    ......
}
```

瞬间恍然大悟：原来只要使用绝对路径就可以指定数据库的路径了啊！
`if (name.charAt(0) == File.separatorChar)`就是判断数据库名是否以`/`开头(android是linux系统，linux的绝对路径都是以`/`开头的)，如果是绝对路径，则提取数据库目录和数据库文件名。如果不是绝对路径，则通过`getDatabasesDir()`方法来获取数据库目录（即`/data/data/PACKAGE_NAME/databases`）。
然后写了一个测试例子，还真是可以通过指定绝对路径给SQLiteOpenHelper来指定数据库路径的。

以上的源码分析是基于**android 5.0**的，测试例子在**android 4.4**上运行。
也就是说至少**android 4.4**之后的版本都是可以指定绝对路径给SQLiteOpenHelper的。至于低版本的系统就没有测试过了。