#!/usr/bin/env lisp
;;;
;;; generated by wxGlade "faked test version"
;;;

(asdf:operate 'asdf:load-op 'wxcl)
(use-package "FFI")
(ffi:default-foreign-language :stdc)


;;; begin wxGlade: dependencies
(use-package :wxCL)
(use-package :wxColour)
(use-package :wxEvent)
(use-package :wxEvtHandler)
(use-package :wxFont)
(use-package :wxFrame)
(use-package :wxSizer)
(use-package :wxTextCtrl)
(use-package :wxWindow)
(use-package :wx_main)
(use-package :wx_wrapper)
;;; end wxGlade

;;; begin wxGlade: extracode
;;; end wxGlade


(defclass MyFrame()
        ((top-window :initform nil :accessor slot-top-window)
        (text-ctrl-1 :initform nil :accessor slot-text-ctrl-1)
        (sizer-1 :initform nil :accessor slot-sizer-1)))

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
        (setf (slot-text-ctrl-1 obj) (wxTextCtrl_Create (slot-top-window obj) wxID_ANY (_"Some Input") -1 -1 -1 -1 wxTE_READONLY))
        ;;; end wxGlade
        )

(defmethod set-properties ((obj MyFrame))
        ;;; begin wxGlade: MyFrame.__set_properties
        (wxFrame_SetTitle (slot-top-window obj) (_"frame_1"))
        (slot-text-ctrl-1 obj).SetMinSize((379, 23))
        (wxWindow_SetBackgroundColour (slot-text-ctrl-1 obj) (wxColour_CreateRGB 0, 255, 127))
        (wxWindow_SetForegroundColour (slot-text-ctrl-1 obj) (wxColour_CreateRGB 255, 0, 0))
        (wxWindow_SetFont (slot-text-ctrl-1 obj) (wxFont_Create 10 wxDEFAULT wxNORMAL wxBOLD 0 "" wxFONTENCODING_DEFAULT))
        (wxWindow_SetFocus (slot-text-ctrl-1 obj))
        ;;; end wxGlade
        )

(defmethod do-layout ((obj MyFrame))
        ;;; begin wxGlade: MyFrame.__do_layout
        (setf (slot-sizer-1 obj) (wxBoxSizer_Create wxVERTICAL))
        (wxSizer_AddWindow (slot-sizer-1 obj) (slot-text-ctrl-1 obj) 1 (logior wxALL wxEXPAND) 5 nil)
        (wxWindow_SetSizer (slot-top-window obj) (slot-sizer-1 obj))
        (wxSizer_Fit (slot-sizer-1 obj) (slot-top-window obj))
        (wxFrame_layout (slot-frame-1 self))
        ;;; end wxGlade
        )

;;; end of class MyFrame


(defun init-func (fun data evt)
        (let ((frame-1 (make-MyFrame)))
        (ELJApp_SetTopWindow (slot-top-window frame-1))
        (wxWindow_Show (slot-top-window frame-1))))
;;; end of class MyApp

    (setf (textdomain) "app") ;; replace with the appropriate catalog name
    (defun _ (msgid) (gettext msgid "app"))


(unwind-protect
    (Eljapp_initializeC (wxclosure_Create #'init-func nil) 0 nil)
    (ffi:close-foreign-library "../miscellaneous/wxc-msw2.6.2.dll"))
