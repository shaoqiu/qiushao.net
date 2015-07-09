Annotation-Processing-Tool基本用法
------

### 1. 什么是`apt`
`Annotation Processing Tool` (注解处理器)简称`apt`,是由 JDK 自带的（1.6 及以上）、供用户编写实现自定义 注解处理逻辑的一系列 API 及编译工具。关于注解的说明可以参考另一篇文章<注解的基本用法>。一般来说，自定义注解是在运行时使用的，通过反射获取`class`上的注解，并进行解析处理，使用`apt`可以让我们在编译前处理注解(其实不仅仅可以处理注解，而是所有的类信息都可以处理，下面会有演示)。官方解释如下：
>  apt is a command-line utility for annotation processing. It includes a set of reflective APIs and supporting infrastructure to process program annotations (JSR 175). These reflective APIs provide a build-time, source-based, read-only view of program structure. They are designed to cleanly model the JavaTM programming language's type system after the addition of generics (JSR 14).
    apt first runs annotation processors that can produce new source code and other files. Next, apt can cause compilation of both original and generated source files, thus easing the development cycle.
    JSR 269, also known as the Language Model API, has two basic pieces: an API that models the Java programming language, and an API for writing annotation processors. This functionality is accessed through new options to the javac command; by including JSR 269 support, javac now acts analogously to the apt command in JDK 5.


### 2. eclipse中怎样使用`apt`
下面通过一个简单的例子来演示`apt`的使用方法。这个例子的目标是：
> 通过定义一个`Annotation`，在编译代码的时候，凡是用该`Annotation`注解过的类，方法，我们都要输出他们的警告信息

step 0 ：新建`java`工程`APTProcessor`， 新建一个包`com.shaoqiu.apt`。

step 1 ：新建一个`Annotation`类`PrintMe`， 代码如下：
```java
package com.shaoqiu.apt;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;

@Retention(RetentionPolicy.RUNTIME)
public @interface PrintMe {
}
```
简单起见，定义了一个空类，仅需标注其使用策略为`RetentionPolicy.SOURCE`。

step 2 ： 新建一个类`APTProcessor` 继承`AbstractProcessor`, 代码如下：
```java
package com.shaoqiu.apt;

import java.util.Set;
import javax.annotation.processing.AbstractProcessor;
import javax.annotation.processing.Messager;
import javax.annotation.processing.RoundEnvironment;
import javax.annotation.processing.SupportedAnnotationTypes;
import javax.lang.model.element.Element;
import javax.lang.model.element.TypeElement;
import javax.tools.Diagnostic;

@SupportedAnnotationTypes(value = { "com.shaoqiu.apt.PrintMe" })
public class APTProcessor extends AbstractProcessor {

	@Override
	public boolean process(Set<? extends TypeElement> annotations, RoundEnvironment env) {
		Messager messager = processingEnv.getMessager();
		for (TypeElement te : annotations) {
			for (Element e : env.getElementsAnnotatedWith(te)) {
				messager.printMessage(Diagnostic.Kind.WARNING, "Printing: " + e.toString(), e);
			}
		}
		return true;
	}
}
```
其中`SupportedAnnotationTypes` 标注这个处理器可以处理的注解类型。这里标注为只可以处理`com.shaoqiu.apt.PrintMe`注解。

step 3 ： 为了使我们的的注解处理器能被调用，需要在工程根目录新建`META-INF/services/javax.annotation.processing.Processor` 文件，文件内容为我们定义的注解处理器的全名，这个例子中为：
```java
com.shaoqiu.apt.APTProcessor
```

step 4 ： 生成`jar`包：
`Export` --> `java` --> `JAR file` 导出配置如下图：
<img src="http://i1.tietuku.com/b40d3360271ce3ed.png">
然后点击`finish`即可导出。

step 5 ： 使用注解处理器
新建JAVA工程`APTTest`。新建`libs`目录，将导出的注解处理器JAR包复制到`libs`目录。
导入刚刚生成的注解处理器的JAR包：右击工程  --> `build path` --> `configure build path` --> `libraries` --> `add jars` 选择刚刚导出的注解处理器JAR包。

启用注解处理器：右击工程 --> `Properties` --> `Java Compiler` --> `Annotation Processing`， 启用`Enable project specific setting`

`Annotation Processing` --> `Factory Path`，启用`Enable project specific setting`，点`Add JARs`添加刚刚导出的注解处理器JAR包。

新建测试类`Main`，代码如下：
```java
import com.shaoqiu.apt.PrintMe;

@PrintMe
public class Main {
	
	public static void main(String[] args) {
		System.out.println("apt test");
	}

	@PrintMe
	public void showPrintInfo() {
	}
	
	public void notShowPrintInfo() {
	}
}
```
保存代码后，就会发现使用了注解的地方都有警告，如图所示：
<img src="http://i1.tietuku.com/502d7eae97d5e9f5.png">

### 3. android studio中怎样使用apt
代码例子就不说了，只说怎样配置使用apt。
首先要明确的是：Android Studio里面有两个`build.gradle`。一个是Module(=Eclipse的project)，一个是Project(=Eclipse的workspace) 

STEP 1：打开Android Studio里Project的build.gradle，加入下面几行： 
```
classpath 'org.robolectric:robolectric-gradle-plugin:0.+'
classpath 'com.neenbedankt.gradle.plugins:android-apt:1.+' 
```

STEP 2：打开Module的build.grade，加入你要使用的带APT注解处理器的jar包： 
文件开头加入依赖:
```
apply plugin:'com.android.application'
apply plugin:'android-apt'
```
加入JAR包：
```
dependencies {
compile files('libs/SimpleDAO.jar')
apt files('libs/SimpleDAO.jar')
}
```