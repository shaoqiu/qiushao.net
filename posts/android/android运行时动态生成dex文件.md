android 运行时动态生成 dex 文件
------
**create time: 2015-07-13; update time: 2015-07-14**

---------------------------------------------------------------

最近在研究 android 插件化开发框架[Android PluginManager](https://github.com/houkx/android-pluginmgr/)。这个框架使用了[dexmaker](https://github.com/crittercism/dexmaker)来动态生成 dex 文件。所以先来学习一下 `dexmaker`的使用方法。需要注意的是  `dexmaker`1.3 版本，使用有问题，提示错误`java.lang.NoClassDefFoundError: com.google.dexmaker.dx.rop.type.Type`，整了大半天也不知道错哪里了，看了这个[issues](https://github.com/crittercism/dexmaker/issues/18)才知道这个版本有问题，但作者好像并没有要修改的意思。所以我使用了[Android PluginManager](https://github.com/houkx/android-pluginmgr/) Demo 的 libs 中`dexmaker-1.1.jar`文件。在继续之前，我们或许应该先了解一下[dex](http://source.android.com/devices/tech/dalvik/index.html)字节码文件的格式（需要翻墙）。

本来想自己写的，但发现 dexmaker 源码中有个 javadoc 目录，发现里面有个简短的教程，就直接翻译算了。

------------------------------------------------------

`public final class DexMaker extends Object`
用于生成可以 Android 上运行的 Dalvik 字节码文件(`.dex`)。`.dex`文件定义了类和接口，包括它们的成员方法，成员变量，可执行代码，还有调试信息。它们也定义了注解，但是目前这个版本的 API 还不支持创建包含注解的`.dex`文件。
这个库主要是为了满足两种情景：
- 运行时生成代码。在你的 Android 应用里使用这个库，你可以动态生成和加载执行代码。这种情景情况适用于使用环境和目标环境都是 Android。
- 编译时生成代码。你可能会在一个 Android 编译器中使用这个库。这种情景下，生成的`.dex`文件必须要安装到 Android 设备上才能运行。

例子：Fibonacci（斐波那契数列）
为了表明应该怎样使用这个 API ，我们将会使用 DexMaker 来生成一个与下面的 java 源代码等价的类：
```java
package com.google.dexmaker.examples;

public class Fibonacci {
	public static int fib(int i) {
		if (i < 2) {
			return i;
		}
		return fib(i - 1) + fib(i - 2);
	}
}
```

我们首先创建一个 `TypeId`用来表示被生成的类。 DexMaker 使用的是内部命名方式来标志类型的，比如`Ljava/land/Object;`，而不是像它们的 java 定义`java.land.Object`。
```java
TypeId<?> fibonacci = TypeId.get("Lcom/google/dexmaker/examples/Fibonacci;");
```
其中`Lcom/google/dexmaker/examples/Fibonacci;`是`com.google.dexmaker.examples.Fibonacii`在字节码中的全限定名称表示。关于这方面的知识可以参考《深入理解java虚拟机》第6.3.5 章节。
接下来，我们声明这个类。我们可以指定这个类型的源文件用于堆栈跟踪，它的访问标志，它的父类，还有它实现的接口。在这个例子中，`Fibonacci`是一个`public`类，继承了`Object`类：
```java
String fileName = "Fibonacci.generated";
DexMaker dexMaker = new DexMaker();
dexMaker.declare(fibonacci, fileName, Modifier.PUBLIC, TypeId.OBJECT);
```
在未定义一个类之前就定义这个类的成员是非法的。
为了能够更方便的将我们的 Java 方法转换成 dex 操作形式，我们需要手动将它转换成类似汇编语言的形式。我们需要使用标志和分支来替换`if`分支和`for`循环这些控制流。我们还要避免在一个语句中进行了多个操作，必要时，我们使用局部变量来分解这些复杂语句。我们可以将上面提到的`Fibonacci`数列的计算方法等价转换如下：
```java
   int constant1 = 1;
   int constant2 = 2;
   if (i < constant2) goto baseCase;
   int a = i - constant1;
   int b = i - constant2;
   int c = fib(a);
   int d = fib(b);
   int result = c + d;
   return result;
 baseCase:
   return i;
```
我们在要声明的类型上找到这个方法的`MethodId`，它定义了方法的返回值类型，它的方法名，它的参数类型。接下来我们声明这个方法，通过使用位操作 `OR` 组合`Modifier`的常量指定它的访问标志。通过调用`declare`，返回一个`Code`对象，我们将使用这个对象来定义我们的操作指令。
```java
MethodId<?, Integer> fib = fibonacci.getMethod(TypeId.INT, "fib", TypeId.INT);
Code code = dexMaker.declare(fib, Modifier.PUBLIC | Modifier.STATIC);
```
需要注意的一个限制是：**所有的局部变量必须定义在任何操作指令之前！**，使用`newLocal`可以创建一个新的局部变量。方法的参数被定义为局部变量，可以使用`getParameter()`来获取传入的参数。对于一个非静态方法来说，可以使用`getThis()`来获取它的`this`指针。接下来我们定义我们的`fib()`方法所需要用到的所有局部变量：
```java
   Local<Integer> i = code.getParameter(0, TypeId.INT);
   Local<Integer> constant1 = code.newLocal(TypeId.INT);
   Local<Integer> constant2 = code.newLocal(TypeId.INT);
   Local<Integer> a = code.newLocal(TypeId.INT);
   Local<Integer> b = code.newLocal(TypeId.INT);
   Local<Integer> c = code.newLocal(TypeId.INT);
   Local<Integer> d = code.newLocal(TypeId.INT);
   Local<Integer> result = code.newLocal(TypeId.INT);
```
需要注意的是，`Local`有一个`Integer`类型参数，这对于生成原始类型（像String和Integer）的代码是有用的，但不能用来生成非原始类型的代码。因此你最好只使用原始类型。（泽注：我们可以这样生成非原始类型的变量`Local<Intent> intent = code.newLocal(TypeId.get(Intent.class));`)。
我们已经准备好开始定义我们的方法的操作指令了。我们可以查看`Code`类，获取所有可用的操作指令及它们的使用方法。
```java
   code.loadConstant(constant1, 1);
   code.loadConstant(constant2, 2);
   Label baseCase = new Label();
   code.compare(Comparison.LT, baseCase, i, constant2);
   code.op(BinaryOp.SUBTRACT, a, i, constant1);
   code.op(BinaryOp.SUBTRACT, b, i, constant2);
   code.invokeStatic(fib, c, a);
   code.invokeStatic(fib, d, b);
   code.op(BinaryOp.ADD, result, c, d);
   code.returnValue(result);
   code.mark(baseCase);
   code.returnValue(i);
```

我们已经定义好`.dex`文件了，我们只要将它写入文件系统或者将其加载到当前进程。在这个例子中，我们将加载生成的代码到当前进程。这只在当前进程是在 Android 设备上运行时适用。我们使用`generateAndLoad()`去生成并加载代码，它需要传入一个 `ClassLoader`作为我们生成的代码的`parent ClassLoader`，它还需要一个目录，以便可以写入临时文件。
```java
ClassLoader loader = dexMaker.generateAndLoad(getClassLoader(), getCacheDir());
```

最后，我们将使用反射加载我们生成的类，并调用它的`fib()`方法：
```java
Class<?> fibonacciClass = loader.loadClass("com.google.dexmaker.examples.Fibonacci");
Method fibMethod = fibonacciClass.getMethod("fib", int.class);
System.out.println(fibMethod.invoke(null, 8));
```

至此我们的 `Fibonacci`类终于完成了。回头看看还是挺复杂的。需要我们将复杂的表达式简化，简化成能够直接转化成汇编代码的形式，也就是相当于我们在直接写汇编代码，只不过是`Dalvik`虚拟机的汇编代码而已。

最后附上完整的代码：
```java
package com.example.dexmaketest;

import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;

import android.app.Activity;
import android.os.Bundle;

import com.google.dexmaker.BinaryOp;
import com.google.dexmaker.Code;
import com.google.dexmaker.Comparison;
import com.google.dexmaker.DexMaker;
import com.google.dexmaker.Label;
import com.google.dexmaker.Local;
import com.google.dexmaker.MethodId;
import com.google.dexmaker.TypeId;

public class MainActivity extends Activity {

	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_main);
		try {
			dexmakerTest();
		} catch (IOException e) {
			e.printStackTrace();
		} catch (IllegalArgumentException e) {
			e.printStackTrace();
		} catch (ClassNotFoundException e) {
			e.printStackTrace();
		} catch (NoSuchMethodException e) {
			e.printStackTrace();
		} catch (IllegalAccessException e) {
			e.printStackTrace();
		} catch (InvocationTargetException e) {
			e.printStackTrace();
		}
	}

	private void dexmakerTest() throws IOException, ClassNotFoundException, NoSuchMethodException, IllegalArgumentException, IllegalAccessException, InvocationTargetException {
		TypeId<?> fibonacci = TypeId
				.get("Lcom/google/dexmaker/examples/Fibonacci;");
		String fileName = "Fibonacci.generated";
		DexMaker dexMaker = new DexMaker();
		dexMaker.declare(fibonacci, fileName, Modifier.PUBLIC, TypeId.OBJECT);

		MethodId<?, Integer> fib = fibonacci.getMethod(TypeId.INT, "fib",
				TypeId.INT);
		Code code = dexMaker.declare(fib, Modifier.PUBLIC | Modifier.STATIC);

		Local<Integer> i = code.getParameter(0, TypeId.INT);
		Local<Integer> constant1 = code.newLocal(TypeId.INT);
		Local<Integer> constant2 = code.newLocal(TypeId.INT);
		Local<Integer> a = code.newLocal(TypeId.INT);
		Local<Integer> b = code.newLocal(TypeId.INT);
		Local<Integer> c = code.newLocal(TypeId.INT);
		Local<Integer> d = code.newLocal(TypeId.INT);
		Local<Integer> result = code.newLocal(TypeId.INT);

		code.loadConstant(constant1, 1);
		code.loadConstant(constant2, 2);
		Label baseCase = new Label();
		code.compare(Comparison.LT, baseCase, i, constant2);
		code.op(BinaryOp.SUBTRACT, a, i, constant1);
		code.op(BinaryOp.SUBTRACT, b, i, constant2);
		code.invokeStatic(fib, c, a);
		code.invokeStatic(fib, d, b);
		code.op(BinaryOp.ADD, result, c, d);
		code.returnValue(result);
		code.mark(baseCase);
		code.returnValue(i);

		ClassLoader loader = dexMaker.generateAndLoad(getClassLoader(), getCacheDir());
		Class<?> fibonacciClass = loader.loadClass("com.google.dexmaker.examples.Fibonacci");
		Method fibMethod = fibonacciClass.getMethod("fib", int.class);
		System.out.println("Fibonacci.fib(8) = " + fibMethod.invoke(null, 8));
	}
}
```