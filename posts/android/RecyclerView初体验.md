RecyclerView初体验
------
**create time: 2015-08-03; update time: 2015-08-03**

---------------------------------------------------------------


android L 中增加了几个新的控件，其中有一个 RecyclerView 控件，感觉非常强大。该控件用于在有限的窗口中展示大量数据集，RecyclerView  顾名思义，就是回收重复利用 View，以节省内在的消耗。只使用这个控件就可以实现 ListView，水平 ListView，GridView，瀑布流这些布局，非常的灵活。

### 1. 为什么使用RecyclerView
#### 1.1.  节省内存消耗
ListView，GridView 也是可以使用回收重复利用View的。 它们都是通过ViewHolder来实现View的重复利用。那这跟 ListView， GridView 有什么区别呢？关于ViewHolder，Google早就推荐开发者使用，不过也只是建议而已，是否使用ViewHolder完全靠开发者的觉悟。但是RecyclerView.Adapter要求开发者必须使用ViewHolder。 

#### 1.2. 灵活
和ListView不一样的是，RecyclerView不再负责Item的摆放等显示方面的功能。所有和布局、绘制等方面的工作Google都其拆分成不同的类进行管理。所以开发者可以自定义各种各样满足定制需求的的功能类。以前想要实现水平列表，瀑布流布局是比较麻烦的，但使用RecyclerView却能很容易的实现。

### 2. RecyclerView 相关的类

- RecyclerView.Adapter ：托管数据集合，为每个Item创建View，其功能与 ListView  的Adapter 功能是一样的。区别在于 RecyclerView.Adapter 强制使用ViewHolder 。
- RecyclerView.ViewHolder：用于回收利用View。
- RecyclerView.LayoutManager：负责Item视图的布局。
- RecyclerView.ItemDecoration：为每个Item视图添加装饰，比如说分隔线
- RecyclerView.ItemAnimator：负责添加、删除数据时的动画效果

相关的类就这么几个，前三个是强制使用的，后面两个可以作为美化效果。

### 3. Example
下面来举几个例子来演示一下RecyclerView灵活，强大的功能。例子基于 android-studio 完成。

#### 3.1. 导入包
RecyclerView 虽说是在android L中增加的，但它是以support library 的形式提供的，所以我们可以在低版本的系统中使用。在 android-studio中只需要在模块的构建脚本 build.gradle 中加入以下配置即可：
```
compile 'com.android.support:recyclerview-v7:22.+'
```
保存，同步之后就可以看到 External Library 中多了 RecyclerView 的包。

#### 3.2. 布局
新建一个布局文件 item.xml 作为数据项的布局，内容如下：
```xml
<?xml version="1.0" encoding="utf-8"?>
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="60dp"
    android:layout_height="60dp"
    android:layout_margin="8dp">

    <TextView
        android:id="@+id/id_num"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:background="#0e000000"
        android:gravity="center" />
</FrameLayout>
```

修改 activity 的布局如下：
```xml
<RelativeLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <android.support.v7.widget.RecyclerView
        android:id="@+id/id_recyclerview"
        android:layout_width="match_parent"
        android:layout_height="match_parent" />

</RelativeLayout>
```

#### 3.3. Adapter and ViewHolder
新建一个类 MyAdapter.java ：
```java
package net.qiushao.recyclerviewtest;

import android.content.Context;
import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import java.util.List;

/**
 * Created by shaoqiu on 15-8-3.
 */
public  class MyAdapter extends RecyclerView.Adapter<MyAdapter.MyViewHolder> {

    private List<String> mDatas;
    private Context mContext;

    public MyAdapter(Context context, List<String> datas) {
        mDatas = datas;
        mContext = context;
    }

    @Override
    public MyViewHolder onCreateViewHolder(ViewGroup viewGroup, int i) {
        MyViewHolder holder = new MyViewHolder(LayoutInflater.from(
                mContext).inflate(R.layout.item, viewGroup, false));
        return holder;
    }

    @Override
    public void onBindViewHolder(MyViewHolder myViewHolder, int i) {
        myViewHolder.tv.setText(mDatas.get(i));
    }

    @Override
    public int getItemCount() {
        return mDatas.size();
    }

    class MyViewHolder extends RecyclerView.ViewHolder {
        TextView tv;

        public MyViewHolder(View view) {
            super(view);
            tv = (TextView) view.findViewById(R.id.id_num);
        }
    }
}
```

#### 3.4. Activity
Activity的代码实现如下：
```java
package net.qiushao.recyclerviewtest;

import android.app.Activity;
import android.os.Bundle;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import java.util.ArrayList;
import java.util.List;

public class MainActivity extends Activity {
    private RecyclerView mRecyclerView;
    private MyAdapter mAdapter;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        mRecyclerView = (RecyclerView) findViewById(R.id.id_recyclerview);
        mRecyclerView.setLayoutManager(new LinearLayoutManager(this));
        mRecyclerView.setAdapter(mAdapter = new MyAdapter(this, initData()));
    }

    protected List<String> initData() {
        List<String> datas = new ArrayList<String>();
        for (int i = 'A'; i <= 'z'; i++) {
            datas.add("" + (char) i);
        }
        return datas;
    }
}
```

至此，一个最简单的RecyclerView的Demo就已经完成了。