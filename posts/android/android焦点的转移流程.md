android焦点的转移流程
------
**create time: 2015-08-11; update time: 2015-08-11**

---------------------------------------------------------------

对于使用触屏操作的手机，平板来说是无所谓焦点的，手指想点哪里就点哪里。但对于TV这种使用遥控来操作的设备，焦点则是非常重要的。当屏幕上可获取焦点的控件很多时，焦点的转移方式，经常不符合我们的需求，所以需要我们加以控制，控制焦点的方法主要有两种
1. requestFocus ：请求焦点，我们想让哪个控件获取焦点，就让它调用 requestFocus方法即可。
2.  指定NextFocus：指定下一个焦点。焦点的转移往往是通过方向键来控制的。有上下左右四个方向键，我们可以分别指定按这些方向键，焦点要转移到哪个控件上。具体为：
- android:nextFocusUp
- android:nextFocusDown
- android:nextFocusLeft
- android:nextFocusRight

这两种方法对于在布局文件上直接布局的控件来说基本上已经满足我们对焦点的控制需求了，但对于 ListView 这类动态添加的控件来说，往往会出现一些意想不到的焦点问题。焦点会乱跳！但由于控件是动态添加的，所以不好使用前面说的方法。正所谓知己知彼，才能百战百胜，为了能控制住焦点转移，我们需要了解它是怎样转移的。

焦点的转移是由按键事件触发的。所以我们得从按键事件入手。当我们按下方向键时，系统开始分发`KeyEvent.KeyCode_DPAD_*`按键事件，最终交给ViewRootImpl.java向APP进行按键分发。ViewRootImpl 有一个内部类 ViewPostImeInputStage，焦点的转移就是在这个内部类的 processKeyEvent 方法中进行的：
```java
private int processKeyEvent(QueuedInputEvent q) {
    final KeyEvent event = (KeyEvent)q.mEvent;
    ......

    // Deliver the key to the view hierarchy.
    if (mView.dispatchKeyEvent(event)) {
        return FINISH_HANDLED;
    }
    ......
```

首先调用 mView.dispatchKeyEvent(event) 进行事件分发，由 DecorView --> ViewGroup --> View 一层一层分发处理，如果某一层消费了这个事件（返回 true），则按键事件处理完成，直接返回了。否则接下来由系统控制焦点的转移：
```java
if (direction != 0) {
    View focused = mView.findFocus();
    if (focused != null) {
        View v = focused.focusSearch(direction);
        if (v != null && v != focused) {
            // do the math the get the interesting rect
            // of previous focused into the coord system of
            // newly focused view
            focused.getFocusedRect(mTempRect);
            if (mView instanceof ViewGroup) {
                ((ViewGroup) mView).offsetDescendantRectToMyCoords(
                    focused, mTempRect);
                ((ViewGroup) mView).offsetRectIntoDescendantCoords(
                    v, mTempRect);
            }
            if (v.requestFocus(direction, mTempRect)) {
                playSoundEffect(SoundEffectConstants
                        .getContantForFocusDirection(direction));
                return FINISH_HANDLED;
            }
        }

        // Give the focused view a last chance to handle the dpad key.
        if (mView.dispatchUnhandledMove(focused, direction)) {
            return FINISH_HANDLED;
        }
    } else {
        // find the best view to give focus to in this non-touch-mode with no-focus
        View v = focusSearch(null, direction);
        if (v != null && v.requestFocus(direction)) {
            return FINISH_HANDLED;
        }
    }
}
```
如果界面上有焦点存在了，则调用 focused.focusSearch 方法去寻找下一个焦点控件。focused 为View 的实例，所以我们看看 View 类的 focusSearch 方法：
```java
    public View focusSearch(int direction) {
        if (mParent != null) {
            return mParent.focusSearch(this, direction);
        } else {
            return null;
        }
    }
```
只是调用了父容器的focusSearch方法来查找。mParent 为 ViewParent 类型，但ViewParent其实只是一个接口而已，并没有具体的实现。在讲解常用布局的时候，我们知道所有的布局容器都继承了 ViewGroup，而 ViewGroup 实现了ViewParent 接口。所以这里的focusSearch方法为ViewGroup 的成员方法，跟进去看一下：
```java
    public View focusSearch(View focused, int direction) {
        if (isRootNamespace()) {
            // root namespace means we should consider ourselves the top of the
            // tree for focus searching; otherwise we could be focus searching
            // into other tabs.  see LocalActivityManager and TabHost for more info
            return FocusFinder.getInstance().findNextFocus(this, focused, direction);
        } else if (mParent != null) {
            return mParent.focusSearch(focused, direction);
        }
        return null;
    }
```

我们发现焦点的查找过程是一层一层地传给父容器处理的，直到根容器 ViewRootImpl 。最后调用了 FocusFinder.getInstance().findNextFocus(this, focused, direction); 来真正进行查找。this 参数就是当前屏幕的根布局。我们跟进去：
```java
    private View findNextFocus(ViewGroup root, View focused, Rect focusedRect, int direction) {
        View next = null;
        if (focused != null) {
            next = findNextUserSpecifiedFocus(root, focused, direction);
        }
        if (next != null) {
            return next;
        }
        ArrayList<View> focusables = mTempList;
        try {
            focusables.clear();
            root.addFocusables(focusables, direction);
            if (!focusables.isEmpty()) {
                next = findNextFocus(root, focused, focusedRect, direction, focusables);
            }
        } finally {
            focusables.clear();
        }
        return next;
    }
```

先调用 findNextUserSpecifiedFocus ，如果开发者有设置focused 控件的 android:nextFocus* 属性的话，且指定的控件可以获取焦点，则使用开发者指定的控件作为next focus。否则先搜集屏幕上所有可以获取焦点的控件，放到一个列表 focusables 中，然后调用 next = findNextFocus(root, focused, focusedRect, direction, focusables); 来计算下一个焦点：
```java
private View findNextFocus(ViewGroup root, View focused, Rect focusedRect,
        int direction, ArrayList<View> focusables) {
    if (focused != null) {
        if (focusedRect == null) {
            focusedRect = mFocusedRect;
        }
        // fill in interesting rect from focused
        focused.getFocusedRect(focusedRect);
        root.offsetDescendantRectToMyCoords(focused, focusedRect);
    } else {
        if (focusedRect == null) {
            focusedRect = mFocusedRect;
            // make up a rect at top left or bottom right of root
            switch (direction) {
                case View.FOCUS_RIGHT:
                case View.FOCUS_DOWN:
                    setFocusTopLeft(root, focusedRect);
                    break;
                case View.FOCUS_FORWARD:
                    if (root.isLayoutRtl()) {
                        setFocusBottomRight(root, focusedRect);
                    } else {
                        setFocusTopLeft(root, focusedRect);
                    }
                    break;

                case View.FOCUS_LEFT:
                case View.FOCUS_UP:
                    setFocusBottomRight(root, focusedRect);
                    break;
                case View.FOCUS_BACKWARD:
                    if (root.isLayoutRtl()) {
                        setFocusTopLeft(root, focusedRect);
                    } else {
                        setFocusBottomRight(root, focusedRect);
                        break;
                    }
            }
        }
    }

    switch (direction) {
        case View.FOCUS_FORWARD:
        case View.FOCUS_BACKWARD:
            return findNextFocusInRelativeDirection(focusables, root, focused, focusedRect,
                    direction);
        case View.FOCUS_UP:
        case View.FOCUS_DOWN:
        case View.FOCUS_LEFT:
        case View.FOCUS_RIGHT:
            return findNextFocusInAbsoluteDirection(focusables, root, focused,
                    focusedRect, direction);
        default:
            throw new IllegalArgumentException("Unknown direction: " + direction);
    }
}
```

首先确定当前焦点框的位置，如果当前有控件获取焦点，则为控件所在的区域，如果没有控件获取焦点，则根据按键，设置为左上角或者右下角。然后调用了findNextFocusInAbsoluteDirection 方法处理：
```java
View findNextFocusInAbsoluteDirection(ArrayList<View> focusables, ViewGroup root, View focused,
        Rect focusedRect, int direction) {
    // initialize the best candidate to something impossible
    // (so the first plausible view will become the best choice)
    mBestCandidateRect.set(focusedRect);
    switch(direction) {
        case View.FOCUS_LEFT:
            mBestCandidateRect.offset(focusedRect.width() + 1, 0);
            break;
        case View.FOCUS_RIGHT:
            mBestCandidateRect.offset(-(focusedRect.width() + 1), 0);
            break;
        case View.FOCUS_UP:
            mBestCandidateRect.offset(0, focusedRect.height() + 1);
            break;
        case View.FOCUS_DOWN:
            mBestCandidateRect.offset(0, -(focusedRect.height() + 1));
    }

    View closest = null;

    int numFocusables = focusables.size();
    for (int i = 0; i < numFocusables; i++) {
        View focusable = focusables.get(i);

        // only interested in other non-root views
        if (focusable == focused || focusable == root) continue;

        // get focus bounds of other view in same coordinate system
        focusable.getFocusedRect(mOtherRect);
        root.offsetDescendantRectToMyCoords(focusable, mOtherRect);

        if (isBetterCandidate(direction, focusedRect, mOtherRect, mBestCandidateRect)) {
            mBestCandidateRect.set(mOtherRect);
            closest = focusable;
        }
    }
    return closest;
}
```

遍历所有的 focusable 控件，在按键方向上，看哪个控件离当前焦点框最近，即为下一个要获取焦点的控件。具体方法就不深究了。下一个焦点控件找到了，我们回到 ViewRootImpl.ViewPostImeInputStage.processKeyEvent 方法中。接下来调用了 v.requestFocus(direction, mTempRect) 让找到的下一个焦点控件请求焦点。经过几层调用，转到View.handleFocusGainInternal 方法中：
```java
    void handleFocusGainInternal(int direction, Rect previouslyFocusedRect) {
        if (DBG) {
            System.out.println(this + " requestFocus()");
        }

        if ((mPrivateFlags & PFLAG_FOCUSED) == 0) {
            mPrivateFlags |= PFLAG_FOCUSED;

            View oldFocus = (mAttachInfo != null) ? getRootView().findFocus() : null;

            if (mParent != null) {
                mParent.requestChildFocus(this, this);
            }

            if (mAttachInfo != null) {
                mAttachInfo.mTreeObserver.dispatchOnGlobalFocusChange(oldFocus, this);
            }

            onFocusChanged(true, direction, previouslyFocusedRect);
            refreshDrawableState();
        }
    }
```
先调用了 mParent.requestChildFocus(this, this);  清理屏幕上的焦点。这个方法里面经过几层的调用，最终会调用当前获取焦点控件的 OnFocusChangeListener.onFocusChange 监听器回调方法，通知 View 已经失去焦点。
然后调用 onFocusChanged(true, direction, previouslyFocusedRect);  这时焦点就完成转移了。最后，刷新 Drawable 。


至此，整个焦点转移的流程就已经走完了。