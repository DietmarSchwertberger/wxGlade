#!/usr/bin/env lisp
;;;
;;; generated by wxGlade "faked test version"
;;;

(asdf:operate 'asdf:load-op 'wxcl)
(use-package "FFI")
(ffi:default-foreign-language :stdc)


;;; begin wxGlade: dependencies
(use-package :wxButton)
(use-package :wxCL)
(use-package :wxColour)
(use-package :wxEvent)
(use-package :wxEvtHandler)
(use-package :wxFrame)
(use-package :wxListBox)
(use-package :wxSizer)
(use-package :wxStaticLine)
(use-package :wxWindow)
(use-package :wx_main)
(use-package :wx_wrapper)
;;; end wxGlade

;;; begin wxGlade: extracode
;;; end wxGlade


(defclass MyDialog()
        ((top-window :initform nil :accessor slot-top-window)
        (list-box-1 :initform nil :accessor slot-list-box-1)
        (sizer-2 :initform nil :accessor slot-sizer-2)
        (button-4 :initform nil :accessor slot-button-4)
        (button-5 :initform nil :accessor slot-button-5)
        (sizer-4 :initform nil :accessor slot-sizer-4)
        (list-box-2 :initform nil :accessor slot-list-box-2)
        (sizer-3 :initform nil :accessor slot-sizer-3)
        (grid-sizer-2 :initform nil :accessor slot-grid-sizer-2)
        (static-line-1 :initform nil :accessor slot-static-line-1)
        (button-2 :initform nil :accessor slot-button-2)
        (button-1 :initform nil :accessor slot-button-1)
        (sizer-1 :initform nil :accessor slot-sizer-1)
        (grid-sizer-1 :initform nil :accessor slot-grid-sizer-1)))

(defun make-MyDialog ()
        (let ((obj (make-instance 'MyDialog)))
          (init obj)
          (set-properties obj)
          (do-layout obj)
          obj))

(defmethod init ((obj MyDialog))
"Method creates the objects contained in the class."
        ;;; begin wxGlade: MyDialog.__init__
        (setf (slot-top-window obj) (wxDialog_create nil wxID_ANY "" -1 -1 -1 -1 wxDEFAULT_DIALOG_STYLE))
        (setf (slot-list-box-1 obj) (wxListBox_Create (slot-top-window obj) wxID_ANY -1 -1 -1 -1 0 (vector ) 0))
        (setf (slot-sizer-2 obj) (StaticBoxSizer_Create (wxStaticBox:wxStaticBox_Create (slot-frame obj) (_"Unassigned Permissions:")) wxHORIZONTAL))
        (setf (slot-button-4 obj) (wxButton_Create (slot-top-window obj) wxID_ADD "" -1 -1 -1 -1 0))
        (setf (slot-button-5 obj) (wxButton_Create (slot-top-window obj) wxID_REMOVE "" -1 -1 -1 -1 0))
        (setf (slot-list-box-2 obj) (wxListBox_Create (slot-top-window obj) wxID_ANY -1 -1 -1 -1 0 (vector ) 0))
        (setf (slot-sizer-3 obj) (StaticBoxSizer_Create (wxStaticBox:wxStaticBox_Create (slot-frame obj) (_"Assigned Permissions:")) wxHORIZONTAL))
        (setf (slot-static-line-1 obj) (wxStaticLine_Create (slot-top-window obj) wxID_ANY -1 -1 -1 -1 0))
        (setf (slot-button-2 obj) (wxButton_Create (slot-top-window obj) wxID_OK "" -1 -1 -1 -1 0))
        (setf (slot-button-1 obj) (wxButton_Create (slot-top-window obj) wxID_CANCEL "" -1 -1 -1 -1 0))
        ;;; end wxGlade
        )

(defmethod set-properties ((obj MyDialog))
        ;;; begin wxGlade: MyDialog.__set_properties
        (wxWindow_SetTitle (slot-dialog-1 self) (_"dialog_1"))
        ;;; end wxGlade
        )

(defmethod do-layout ((obj MyDialog))
        ;;; begin wxGlade: MyDialog.__do_layout
        (setf (slot-grid-sizer-1 obj) (wxGridSizer_Create 3 1 0 0))
        (setf (slot-sizer-1 obj) (wxBoxSizer_Create wxHORIZONTAL))
        (setf (slot-grid-sizer-2 obj) (wxGridSizer_Create 1 3 0 0))
        (setf (slot-sizer-4 obj) (wxGridSizer_Create 4 1 0 0))
        (wxSizer_AddWindow (slot-sizer-2 obj) (slot-list-box-1 obj) 1 (logior wxALL wxEXPAND) 5 nil)
        (wxSizer_AddSizer (slot-grid-sizer-2 obj) (slot-sizer-2 obj) 1 wxEXPAND 0 nil)
        (wxSizer_AddWindow (slot-sizer-4 obj) ((20, 20) obj) 0 wxEXPAND 0 nil)
        (wxSizer_AddWindow (slot-sizer-4 obj) (slot-button-4 obj) 0 wxALL 5 nil)
        (wxSizer_AddWindow (slot-sizer-4 obj) (slot-button-5 obj) 0 wxALL 5 nil)
        (wxSizer_AddWindow (slot-sizer-4 obj) ((20, 20) obj) 0 wxEXPAND 0 nil)
        (wxFlexGridSizer_AddGrowableRow (slot-sizer-4 obj) 0)
        (wxFlexGridSizer_AddGrowableRow (slot-sizer-4 obj) 3)
        (wxSizer_AddSizer (slot-grid-sizer-2 obj) (slot-sizer-4 obj) 1 (logior wxEXPAND wxALIGN_CENTER_HORIZONTAL wxALIGN_CENTER_VERTICAL) 0 nil)
        (wxSizer_AddWindow (slot-sizer-3 obj) (slot-list-box-2 obj) 1 (logior wxALL wxEXPAND) 5 nil)
        (wxSizer_AddSizer (slot-grid-sizer-2 obj) (slot-sizer-3 obj) 1 wxEXPAND 0 nil)
        (wxFlexGridSizer_AddGrowableRow (slot-grid-sizer-2 obj) 0)
        (wxFlexGridSizer_AddGrowableCol (slot-grid-sizer-2 obj) 0)
        (wxFlexGridSizer_AddGrowableCol (slot-grid-sizer-2 obj) 2)
        (wxSizer_AddSizer (slot-grid-sizer-1 obj) (slot-grid-sizer-2 obj) 1 wxEXPAND 0 nil)
        (wxSizer_AddWindow (slot-grid-sizer-1 obj) (slot-static-line-1 obj) 0 (logior wxALL wxEXPAND) 5 nil)
        (wxSizer_AddWindow (slot-sizer-1 obj) (slot-button-2 obj) 0 wxALL 5 nil)
        (wxSizer_AddWindow (slot-sizer-1 obj) (slot-button-1 obj) 0 wxALL 5 nil)
        (wxSizer_AddSizer (slot-grid-sizer-1 obj) (slot-sizer-1 obj) 1 (logior wxEXPAND wxALIGN_RIGHT) 0 nil)
        (wxWindow_SetSizer (slot-frame obj) (slot-grid-sizer-1 obj))
        (wxSizer_Fit (slot-grid-sizer-1 obj) (slot-frame obj))
        (wxFlexGridSizer_AddGrowableRow (slot-grid-sizer-1 obj) 0)
        (wxFlexGridSizer_AddGrowableCol (slot-grid-sizer-1 obj) 0)
        (wxWindow_layout (slot-dialog-1 self))
        ;;; end wxGlade
        )

;;; end of class MyDialog


(defun init-func (fun data evt)
        (let ((dialog-1 (make-MyDialog)))
        (ELJApp_SetTopWindow (slot-top-window dialog-1))
        (wxWindow_Show (slot-top-window dialog-1))))
;;; end of class MyApp

    (setf (textdomain) "app") ;; replace with the appropriate catalog name
    (defun _ (msgid) (gettext msgid "app"))


(unwind-protect
    (Eljapp_initializeC (wxclosure_Create #'init-func nil) 0 nil)
    (ffi:close-foreign-library "../miscellaneous/wxc-msw2.6.2.dll"))
