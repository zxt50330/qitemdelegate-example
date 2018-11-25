It has become clear that using QItemDelegates when building lists of things in [Qt for Python](https://www.qt.io/qt-for-python) is to become something of a pattern in my tinkering, and therefore I thought to share a simple sketch of an implementation that has been useful for me...

QListViews complemented by QItemDelegates and QItemModels seemed very daunting to me at first, terribly so, though now I find them somewhat elegant and pleasant to use—even if they seem overwrought at times.

Included in the example are extra methods on the QListView and QItemModel classes that are can be used to insert, delete, and otherwise modify the view/model after its initial instantiation—features which aren't implemented in this example application in an effort to keep things as simple as possible.

Please let me know if there are better ways to do things (especially when painting the list items), I would love to learn how to become a more proper and effective Qt and/or Python person.

    python main.py

<img src="/screenshots/screenshot_mac.png" alt="Screenshot of example application on a Mac" width="500" />

The example was made with PySide2 (Qt for Python) 5.12 (1544803950) and Python 3.7.1.
