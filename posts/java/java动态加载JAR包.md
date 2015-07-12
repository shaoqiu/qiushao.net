java动态加载JAR包
------
**create time: 2015-07-10; update time: 2015-07-12**

---------------------------------------------------------------

### 1. why
在开发过程中有时候会遇到一些需要经常变化的逻辑，甚至一些功能需要增减。按常规的开发模式的话，功能逻辑变化或者功能增减都需要更新整个应用。但有时候更新整个应用，是一件麻烦的事。需要走各种流程，审核。所以我们把部分经常需要变化的功能模块提取出来，作为插件。当这部分逻辑有变化时，只需要更新插件就可以了。我们可以把插件放到服务器上，客户端每次启动都检查一下服务器的插件是否有更新，有更新的话就下载替换本地的插件即可。这样就能很灵活的更新了。

### 2. how
上面讨论了插件化开发的理由，那我们怎么去实现这样的框架呢？我们可以将程序划分为三个部分：`接口`，`宿主程序`，`插件`。接口作为宿主程序和插件通讯的桥梁。宿主程序要能和插件进行通信，必须共同遵守某种协议。这个协议应该由宿主程序来规定。宿主程序应该规定通讯接口，及各种约定：
- 所有插件都必须实现宿主程序提供的接口。
- 插件的命名约定：类的全名_版本号.jar（如"com.shaoqiu.shape.Circle_0.01.jar"），类的全名必须是实现了宿主程序接口的类。
- 插件发布时不能将宿主提供的接口JAR文件一起打包（避免冲突，减少体积）。

好了，有以上的约定就可以开始了。下面我们就来举个小例子来讨论一下。
#### 2.1. 首先由宿主程序提供一个接口
新建一个 JAVA 工程**Host**，作为宿主工程，创建一个包`com.shaoqiu.shape`，在这个包下面创建一个接口。<br/>
`Shape.java`：
```java
package com.shaoqiu.shape;
public interface Shape {
	public void getShapeName();
}
```
这就是宿主程序提供的接口，这个接口是一个形状，有一个方法用来打印自己的形状名称。将这个接口导出为一个`jar`文件，名为`shape.jar`，后面的插件开发都需要导入这个`jar`文件。导出的时候记得只选与接口相关的文件！此处只选`com.shaoqiu.shape`包。

#### 2.2. 实现插件
新建另一个 JAVA 工程**Circle**，作为插件工程，导入上面的`shape.jar`。创建一个包`com.shaoqiu.shape.circle`，在这包下面并创建以下文件。<br/>
`Circle.java`：
```java
package com.shaoqiu.shape.circle;
import com.shaoqiu.shape.Shape;

public class Circle implements Shape{
	@Override
	public String getShapeName() {
		return "Circle";
	}
}
```
将这个工程导出为`com.shaoqiu.shape.circle.Circle_0.01.jar`，导出的时候记得**不要勾选`shape.jar`还有`.classpath`和`.project`文件**，这样我们的第一个插件就已经完成了。

#### 2.2. 实现宿主程序
回到宿主工程**Host**，创建一个包`com.shaoqiu.host`，在这个包下面创建以下文件。 <br/>
`Main.java`：
```java
package com.shaoqiu.host;

import java.io.File;
import java.net.URL;
import java.net.URLClassLoader;

import com.shaoqiu.shape.Shape;

public class Main {
	public static void main(String[] args){
		System.out.println("running in host...");
		String urlPattern = "file:///";
        String pluginPath = "plugins";

        File plugin = new File(pluginPath);
        File[] jarList = plugin.listFiles();

        ClassLoader cl = null;
        String jarPath = null;
        String className = null;
        try {
            for (File jar : jarList) {
                className = jar.getName().split("_")[0];
                jarPath = urlPattern + jar.getAbsolutePath();
                cl = new URLClassLoader(new URL[] { new URL(jarPath) });
                Class<?> c = cl.loadClass(className);
                Shape impl = (Shape) c.newInstance();
                System.out.println(impl.getShapeName());
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
	}
}

```

我们的插件目录为`plugins"`，所以需要在**Host**工程目录下创建一个`plugins`目录，将前面导出的`com.shaoqiu.shape.circle.Circle_0.01.jar`插件放到`plugins`目录。执行宿主程序就可以看到：
```
running host...
Circle
```
可以看到宿主程序成功调用了`Circle`插件的方法。

### 3. Android中动态加载JAR包
android 的应用程序是使用 java 语言来开发的，所以在 android 中也同样可以动态加载 JAR 包。但是 android 的虚拟机与 java 虚拟机是有点区别的，它们所识别的文件格式是不一样的。android 中需要通过dx工具来优化转换成Dalvik byte code才行。下面举一个简单的例子来说明Android中如何动态加载JAR包。

#### 3.1. 实现 android 宿主应用
这里就直接使用上面的`Shape`接口来做演示。新建一个 android 工程`AndroidHost`。将上面导出的`shape.jar`文件复制到`libs`目录下。

修改布局文件如下：<br/>
`activity_main.xml`：
```xml 
<RelativeLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:paddingBottom="@dimen/activity_vertical_margin"
    android:paddingLeft="@dimen/activity_horizontal_margin"
    android:paddingRight="@dimen/activity_horizontal_margin"
    android:paddingTop="@dimen/activity_vertical_margin"
    tools:context="com.example.androidtest.MainActivity" >

    <TextView
        android:id="@+id/text"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="@string/hello_world" />
    
    <Button 
        android:id="@+id/button"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_below="@id/text"
        android:text="load plugins"
        />

</RelativeLayout>
```

修改`MainActivity.java`文件如下：
```java
package com.example.androidtest;

import java.io.File;

import com.shaoqiu.shape.Shape;

import dalvik.system.DexClassLoader;
import android.app.Activity;
import android.content.Context;
import android.os.Bundle;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.Button;
import android.widget.TextView;

public class MainActivity extends Activity {

	private TextView textView;
	private Button load;

	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_main);

		textView = (TextView) findViewById(R.id.text);
		load = (Button) findViewById(R.id.button);
		load.setOnClickListener(new OnClickListener() {

			@Override
			public void onClick(View v) {
				System.out.println("click load");
				File pluginPath = getDir("plugins", Context.MODE_PRIVATE);
				File[] pluginsPath = pluginPath.listFiles();
				for (File plugin : pluginsPath) {
					System.out.println("find plugin : " + plugin.getName());
					DexClassLoader cl = new DexClassLoader(
							plugin.getAbsolutePath(),
							getCacheDir().getAbsolutePath(), null,
							getClassLoader());
					try {
						Class<?> claz = cl.loadClass(plugin.getName().split("_")[0]);
						Shape impl = (Shape) claz.newInstance();
						System.out.println(impl.getShapeName());
						textView.setText(impl.getShapeName());
					} catch (ClassNotFoundException e) {
						e.printStackTrace();
					} catch (InstantiationException e) {
						e.printStackTrace();
					} catch (IllegalAccessException e) {
						e.printStackTrace();
					}
				}
			}
		});
	}
}
```

对比一下加载 JAR 的逻辑，其实跟普通 java 逻辑是差不多的，不同的地方在于android 中使用的是**DexClassLoader**，而不是**URLClassLoader**。`DexClassLoader`的构造函数原型为： `DexClassLoader(String dexPath, String optimizedDirectory, String 
 libraryPath, ClassLoader parent)` 。
 - `dexPath`：为插件的路径，这里设置为`getDir("plugins", Context.MODE_PRIVATE)`。
 - `optimizedDirectory`：为插件的解压路径，这里设置为`getCacheDir().getAbsolutePath()`即`/data/data/com.shaoqiu.androidhost/cache`目录。
 - `libraryPath`：为动态库（SO库）的路径，这里没有使用到动态库，所以设置了null。
 - `ClassLoader`：为该类装载器的父装载器，一般用当前执行类的装载器

到此宿主程序就已经完成了。运行一上宿主程序。然后去`/data/data/com.example.androidtest`目录下，发现多了一个`app_plugins`子目录。这个目录就是通过`getDir("plugins", Context.MODE_PRIVATE)`创建的。也就是说我们的插件应该要放在这个目录。

#### 3.2. 插件的实现
直接使用上面开发的`com.shaoqiu.shape.circle.Circle_0.01.jar`插件吧。不过这个插件需要先经过`dx`处理：
```
dx --dex --output=com.shaoqiu.shape.circle.Circle_0.01.dex.jar com.shaoqiu.shape.circle.Circle_0.01.jar
```
执行这个命令后就地生成`com.shaoqiu.shape.circle.Circle_0.01.dex.jar`文件，通过`adb`命令，将这个文件上传到宿主程序插件目录：
```
adb push com.shaoqiu.shape.circle.Circle_0.01.dex.jar /data/data/com.example.androidtest/app_plugins
```

这时再去执行宿主程序，就会发现输出如下：
```
07-12 05:15:36.725: I/System.out(1619): click load
07-12 05:15:36.726: I/System.out(1619): find plugin : com.shaoqiu.shape.circle.Circle_0.01.dex.jar
07-12 05:15:37.311: I/System.out(1619): Circle
```
android 宿主程序成功调用了`Circle`插件的方法。
不过这种方法只适合于纯粹的逻辑插件，并不适用于UI的插件。实现UI插件的方法比较复杂，以后再讨论。这里先提两个UI插件的框架：
- [DynamicPlugin](https://github.com/zxfrdas/DynamicPlugin.git)：一个同事（我导师）开发的框架，是基于`View`的，即每一个插件就是一个`View`。公司几个项目使用到了这个框架。
- [dynamic-load-apk](https://github.com/singwhatiwanna/dynamic-load-apk.git)：这个框架是基于 android 四大组件的。目前只支持 `Activity`，作者称未来会支持其他组件。

android UI 插件的实现理论及方法后续再详细介绍。