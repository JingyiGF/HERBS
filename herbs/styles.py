class Styles(object):
    def __init__(self):

        self.text_combo_list_style = '''
            QListView {
                background: #656565;
                border: 1px solid gray;
                color: white;
                border-radius: 0px;
            }
        
            QListView::item {
                border: None;
                background: transparent;
                margin:3px;
                height: 24px;
            }                             
        
            QListView::item:selected { 
                border: None;
                margin:3px;
                color: white;
                background: #232323; 
                height: 24px;
            }
        
            QListView::item:selected:!active {
                background: #323232;
                border: None;
            }
        
            QListView::item:selected:active {
                background: #323232;
                border: None;
            }
        
            QListView::item:hover {
                background: #323232;
                border: None;
            }
        '''

        self.text_combo_style = '''
            /*---------------------- QComboBox -----------------------*/
            QComboBox {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                selection-background-color: transparent;
                color: white;
                background-color: transparent;
                border: None;
                border-radius: 5px;
                padding: 0px 0px 0px 5px;
                margin: 0px;
            }
            
            QComboBox:item {
                background: #323232;
                color: white;
                min-height: 10px;
                margin: 0px;
            }
            
            QComboBox:item:selected
            {
                border: None;
                background: #232323;
                margin: 0px;
            }
            
            
            QComboBox:editable {
                background: transparent;
            }
            
            QComboBox:!editable, QComboBox::drop-down:editable {
                 background: #656565;
            }
            
            /* QComboBox gets the "on" state when the popup is open */
            QComboBox:!editable:on, QComboBox::drop-down:editable:on {
                background: transparent;
            }
            
            QComboBox:on { /* shift the text when the popup opens */
                padding: 3px;
                color: white;
                background-color: transparent;
                selection-background-color: transparent;
            }
            
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-top: None;
                border-bottom: None;
                border-left-width: 1px;
                border-left-color: transparent;
                border-left-style: solid; /* just a single line */
                border-top-right-radius: 3px; /* same radius as the QComboBox */
                border-bottom-right-radius: 3px;
            }
            
            QComboBox::down-arrow {
                image: url(icons/tdown.svg);
                width: 13px;
                height: 14px;
                padding-right: 3px;
            }
            
            QComboBox::down-arrow:on { /* shift the arrow when popup is open */
                top: 1px;
                left: 1px;
            }
            
            QComboBox QAbstractItemView {
                border: 2px solid darkgray;
            }
            
            QComboBox QListView {
                background: #656565;
                border: 1px solid gray;
                color: white;
                border-radius: 0px;
            }
        
            QComboBox QListView::item {
                border: None;
                background: transparent;
                margin:3px;
                height: 24px;
            }                             
        
            QComboBox QListView::item:selected { 
                border: None;
                margin:3px;
                color: white;
                background: #232323; 
                height: 24px;
            }
        
            QComboBox QListView::item:selected:!active {
                background: #323232;
                border: None;
            }
        
            QComboBox QListView::item:selected:active {
                background: #323232;
                border: None;
            }
        
            QComboBox QListView::item:hover {
                background: #323232;
                border: None;
            }

        '''

        self.tab_style = '''
            /*---------------------- QTabWidget -----------------------*/
            QTabWidget{
                background-color: rgb(50, 50, 50);
                margin-bottom: 0px;
    
            }
    
            QTabWidget::pane {
                background-color: transparent;
                margin-left: 0px;
                padding-left:0px;
                border-top: 1px solid #747a80;
                border-left: 1px solid #747a80;
                border-right: 1px solid #747a80;
                border-bottom: 1px solid #747a80;
                margin-bottom: 0px;
            }
    
            QTabWidget::tab-bar {
                bottom: 0;
                border: 1px solid gray;
            }
    
            QTabBar::tab {
                background-color: #3c3f41;
                height:30px;
                width: 30px;
                border-bottom: 3px solid #323232;
                margin: 0px;
                padding-top: 5px;
                padding-left: 6px;
            }
    
            QTabBar::tab:selected {
                background: #4e5254;
                border-bottom: 3px solid #747a80;
            }
    
            QTabBar::tab:hover{
                background: #27292a;
            }
    
            QGroupBox {
                background-color: transparent; 
                color: white;
                border: 1px solid; 
                border-radius: 5px; 
                padding-top: 3px; 
                padding-bottom: 3px; 
                margin-top: 0px
            }
    
            QLabel {
                color: white;
            }
    
            /* --------------------------------------- QScrollBar  -----------------------------------*/
            QScrollBar:horizontal
            {
                height: 15px;
                margin: 3px 15px 3px 15px;
                border: None;
                border-radius: 4px;
                background-color: transparent;
            }
    
            QScrollBar::handle:horizontal
            {
                background-color: #656565;
                min-width: 5px;
                border-radius: 4px;
            }
    
            QScrollBar::add-line:horizontal
            {
                margin: 0px 3px 0px 3px;
                width: 10px;
                height: 10px;
                subcontrol-position: right;
                subcontrol-origin: margin;
                border: None;
            }
    
            QScrollBar::sub-line:horizontal
            {
                margin: 0px 3px 0px 3px;
                height: 10px;
                width: 10px;
                subcontrol-position: left;
                subcontrol-origin: margin;
                border: None;
            }
    
            QScrollBar::add-line:horizontal:hover,QScrollBar::add-line:horizontal:on
            {
                height: 10px;
                width: 10px;
                subcontrol-position: right;
                subcontrol-origin: margin;
                border: None;
            }
    
    
            QScrollBar::sub-line:horizontal:hover, QScrollBar::sub-line:horizontal:on
            {
                height: 10px;
                width: 10px;
                subcontrol-position: left;
                subcontrol-origin: margin;
                border: None;
            }
    
            QScrollBar::up-arrow:horizontal, QScrollBar::down-arrow:horizontal
            {
                background: transparent;
            }
    
    
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal
            {
                background: transparent;
            }
    
            QScrollBar:vertical
            {
                background-color: transparent;
                width: 15px;
                margin: 15px 3px 15px 3px;
                border: None;
                border-radius: 4px;
            }
    
            QScrollBar::handle:vertical
            {
                background-color: #656565;
                min-height: 5px;
                border-radius: 4px;
            }
    
            QScrollBar::sub-line:vertical
            {
                margin: 3px 0px 3px 0px;
                height: 10px;
                width: 10px;
                subcontrol-position: top;
                subcontrol-origin: margin;
                border: None;
            }
    
            QScrollBar::add-line:vertical
            {
                margin: 3px 0px 3px 0px;
                height: 10px;
                width: 10px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
                border: None;
            }
    
            QScrollBar::sub-line:vertical:hover,QScrollBar::sub-line:vertical:on
            {
                height: 10px;
                width: 10px;
                subcontrol-position: top;
                subcontrol-origin: margin;
                border: None;
            }
    
            QScrollBar::add-line:vertical:hover, QScrollBar::add-line:vertical:on
            {
                height: 10px;
                width: 10px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
                border: None;
            }
    
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical
            {
                background: transparent;
            }
    
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical
            {
                background: transparent;
            }
        '''

        self.sidebar_title_label_style = '''
            QLabel{
                color: white;
                background: #747a80;
                width: 300px;
                height: 20px;
                padding-bottom: 5px;
                padding-left: 5px;
                padding-top: 2px;
            }
        '''