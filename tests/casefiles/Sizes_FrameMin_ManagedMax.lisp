#!/usr/bin/env lisp
;;;
;;; generated by wxGlade 1.0.1 on Sat Jan  2 23:51:56 2021
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
(use-package :wxPanel)
(use-package :wxSizer)
(use-package :wxWindow)
(use-package :wx_main)
(use-package :wx_wrapper)
;;; end wxGlade

;;; begin wxGlade: extracode
;;; end wxGlade


(defclass MyFrame()
        ((top-window :initform nil :accessor slot-top-window)
        (panel-1 :initform nil :accessor slot-panel-1)
        (sizer-1 :initform nil :accessor slot-sizer-1)
        (sizer-2 :initform nil :accessor slot-sizer-2)
        (button-1 :initform nil :accessor slot-button-1)
        (button-2 :initform nil :accessor slot-button-2)
        (button-3 :initform nil :accessor slot-button-3)
        (sizer-3 :initform nil :accessor slot-sizer-3)
        (button-22 :initform nil :accessor slot-button-22)
        (button-23 :initform nil :accessor slot-button-23)
        (button-24 :initform nil :accessor slot-button-24)
        (sizer-4 :initform nil :accessor slot-sizer-4)
        (button-31 :initform nil :accessor slot-button-31)
        (button-32 :initform nil :accessor slot-button-32)
        (button-33 :initform nil :accessor slot-button-33)
        (sizer-6 :initform nil :accessor slot-sizer-6)
        (button-220 :initform nil :accessor slot-button-220)
        (button-221 :initform nil :accessor slot-button-221)
        (button-222 :initform nil :accessor slot-button-222)))

(defun make-MyFrame ()
        (let ((obj (make-instance 'MyFrame)))
          (init obj)
          (set-properties obj)
          (do-layout obj)
          obj))

(defmethod init ((obj MyFrame))
"Method creates the objects contained in the class."
        ;;; begin wxGlade: MyFrame.__init__
        (setf (slot-top-window obj) (wxFrame_create nil wxID_ANY "" -1 -1 -1 -1 wxDEFAULT_FRAME_STYLE))
        (slot-top-window obj).wxWindow_SetSize((1450, 341))
        (slot-top-window obj).SetMinSize((100, 100))
        (wxFrame_SetTitle (slot-top-window obj) "frame")
        
        (setf (slot-panel-1 obj) (wxPanel_Create (slot-top-window obj) wxID_ANY -1 -1 -1 -1 wxTAB_TRAVERSAL))
        
        (setf (slot-sizer-1 obj) (wxBoxSizer_Create wxHORIZONTAL))
        
        (setf (slot-sizer-2 obj) (wxBoxSizer_Create wxVERTICAL))
        (wxSizer_AddSizer (slot-sizer-1 obj) (slot-sizer-2 obj) 1 wxEXPAND 0 nil)
        
        (setf (slot-button-1 obj) (wxButton_Create (slot-panel-1 obj) wxID_ANY "-/-" -1 -1 -1 -1 0))
        (wxSizer_AddWindow (slot-sizer-2 obj) (slot-button-1 obj) 0 0 0 nil)
        
        (setf (slot-button-2 obj) (wxButton_Create (slot-panel-1 obj) wxID_ANY "button_2 prop 1" -1 -1 -1 -1 0))
        (wxSizer_AddWindow (slot-sizer-2 obj) (slot-button-2 obj) 1 wxFIXED_MINSIZE 0 nil)
        
        (setf (slot-button-3 obj) (wxButton_Create (slot-panel-1 obj) wxID_ANY "button_3 expand" -1 -1 -1 -1 0))
        (wxSizer_AddWindow (slot-sizer-2 obj) (slot-button-3 obj) 0 wxEXPAND 0 nil)
        
        (setf (slot-sizer-3 obj) (wxBoxSizer_Create wxVERTICAL))
        (wxSizer_AddSizer (slot-sizer-1 obj) (slot-sizer-3 obj) 1 wxEXPAND 0 nil)
        
        (setf (slot-button-22 obj) (wxButton_Create (slot-panel-1 obj) wxID_ANY "size/-" -1 -1 -1 -1 0))
        (slot-button-22 obj).SetMinSize((200, 30))
        (wxSizer_AddWindow (slot-sizer-3 obj) (slot-button-22 obj) 0 0 0 nil)
        
        (setf (slot-button-23 obj) (wxButton_Create (slot-panel-1 obj) wxID_ANY "button_23" -1 -1 -1 -1 0))
        (slot-button-23 obj).SetMinSize((200, 30))
        (wxSizer_AddWindow (slot-sizer-3 obj) (slot-button-23 obj) 1 0 0 nil)
        
        (setf (slot-button-24 obj) (wxButton_Create (slot-panel-1 obj) wxID_ANY "button_24" -1 -1 -1 -1 0))
        (slot-button-24 obj).SetMinSize((200, 30))
        (wxSizer_AddWindow (slot-sizer-3 obj) (slot-button-24 obj) 0 wxEXPAND 0 nil)
        
        (setf (slot-sizer-4 obj) (wxBoxSizer_Create wxVERTICAL))
        (wxSizer_AddSizer (slot-sizer-1 obj) (slot-sizer-4 obj) 1 wxEXPAND 0 nil)
        
        (setf (slot-button-31 obj) (wxButton_Create (slot-panel-1 obj) wxID_ANY "size/max" -1 -1 -1 -1 0))
        (slot-button-31 obj).SetMinSize((200, 30))
        (slot-button-31 obj).SetMaxSize((300, 40))
        (wxSizer_AddWindow (slot-sizer-4 obj) (slot-button-31 obj) 0 0 0 nil)
        
        (setf (slot-button-32 obj) (wxButton_Create (slot-panel-1 obj) wxID_ANY "button_32" -1 -1 -1 -1 0))
        (slot-button-32 obj).SetMinSize((200, 30))
        (slot-button-32 obj).SetMaxSize((300, 40))
        (wxSizer_AddWindow (slot-sizer-4 obj) (slot-button-32 obj) 1 0 0 nil)
        
        (setf (slot-button-33 obj) (wxButton_Create (slot-panel-1 obj) wxID_ANY "button_33" -1 -1 -1 -1 0))
        (slot-button-33 obj).SetMinSize((200, 30))
        (slot-button-33 obj).SetMaxSize((300, 40))
        (wxSizer_AddWindow (slot-sizer-4 obj) (slot-button-33 obj) 0 wxEXPAND 0 nil)
        
        (setf (slot-sizer-6 obj) (wxBoxSizer_Create wxVERTICAL))
        (wxSizer_AddSizer (slot-sizer-1 obj) (slot-sizer-6 obj) 1 wxEXPAND 0 nil)
        
        (setf (slot-button-220 obj) (wxButton_Create (slot-panel-1 obj) wxID_ANY "-/max" -1 -1 -1 -1 0))
        (slot-button-220 obj).SetMaxSize((300, 40))
        (wxSizer_AddWindow (slot-sizer-6 obj) (slot-button-220 obj) 0 0 0 nil)
        
        (setf (slot-button-221 obj) (wxButton_Create (slot-panel-1 obj) wxID_ANY "button_221" -1 -1 -1 -1 0))
        (slot-button-221 obj).SetMaxSize((300, 40))
        (wxSizer_AddWindow (slot-sizer-6 obj) (slot-button-221 obj) 1 0 0 nil)
        
        (setf (slot-button-222 obj) (wxButton_Create (slot-panel-1 obj) wxID_ANY "button_222" -1 -1 -1 -1 0))
        (slot-button-222 obj).SetMaxSize((300, 40))
        (wxSizer_AddWindow (slot-sizer-6 obj) (slot-button-222 obj) 0 wxEXPAND 0 nil)
        
        (wxWindow_SetSizer (slot-panel-1 obj) (slot-sizer-1 obj))
        
        (wxFrame_layout (slot-frame self))
        ;;; end wxGlade
        )

;;; end of class MyFrame


(defun init-func (fun data evt)
        (let ((frame (make-MyFrame)))
        (ELJApp_SetTopWindow (slot-top-window frame))
        (wxWindow_Show (slot-top-window frame))))
;;; end of class MyApp


(unwind-protect
    (Eljapp_initializeC (wxclosure_Create #'init-func nil) 0 nil)
    (ffi:close-foreign-library "../miscellaneous/wxc-msw2.6.2.dll"))
