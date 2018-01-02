#!/usr/bin/env lisp
;;;
;;; generated by wxGlade "faked test version"
;;;

(asdf:operate 'asdf:load-op 'wxcl)
(use-package "FFI")
(ffi:default-foreign-language :stdc)


;;; begin wxGlade: dependencies
(use-package :wxCL)
(use-package :wxCheckListBox)
(use-package :wxColour)
(use-package :wxEvent)
(use-package :wxEvtHandler)
(use-package :wxFrame)
(use-package :wxListBox)
(use-package :wxSizer)
(use-package :wxWindow)
(use-package :wx_main)
(use-package :wx_wrapper)
;;; end wxGlade

;;; begin wxGlade: extracode
;;; end wxGlade


(defclass Frame194()
        ((top-window :initform nil :accessor slot-top-window)
        (list-box-single :initform nil :accessor slot-list-box-single)
        (list-box-multiple :initform nil :accessor slot-list-box-multiple)
        (list-box-extended :initform nil :accessor slot-list-box-extended)
        (check-list-box-single :initform nil :accessor slot-check-list-box-single)
        (check-list-box-multiple :initform nil :accessor slot-check-list-box-multiple)
        (check-list-box-extended :initform nil :accessor slot-check-list-box-extended)
        (sizer-1 :initform nil :accessor slot-sizer-1)))

(defun make-Frame194 ()
        (let ((obj (make-instance 'Frame194)))
          (init obj)
          (set-properties obj)
          (do-layout obj)
          obj))

(defmethod init ((obj Frame194))
"Method creates the objects contained in the class."
        ;;; begin wxGlade: Frame194.__init__
        (slot-top-window obj).wxWindow_SetSize((800, 600))
        (setf (slot-list-box-single obj) (wxListBox_Create (slot-top-window obj) wxID_ANY -1 -1 -1 -1 1 (vector (_"Listbox wxLB_SINGLE")) wxLB_SINGLE))
        (setf (slot-list-box-multiple obj) (wxListBox_Create (slot-top-window obj) wxID_ANY -1 -1 -1 -1 1 (vector (_"Listbox wxLB_MULTIPLE")) wxLB_MULTIPLE))
        (setf (slot-list-box-extended obj) (wxListBox_Create (slot-top-window obj) wxID_ANY -1 -1 -1 -1 1 (vector (_"Listbox wxLB_EXTENDED")) wxLB_EXTENDED))
        (setf (slot-check-list-box-single obj) (wxCheckListBox_Create (slot-top-window obj) wxID_ANY -1 -1 -1 -1 1 (vector (_"CheckListBox wxLB_SINGLE")) wxLB_SINGLE))
        (setf (slot-check-list-box-multiple obj) (wxCheckListBox_Create (slot-top-window obj) wxID_ANY -1 -1 -1 -1 1 (vector (_"CheckListBox wxLB_MULTIPLE")) wxLB_MULTIPLE))
        (setf (slot-check-list-box-extended obj) (wxCheckListBox_Create (slot-top-window obj) wxID_ANY -1 -1 -1 -1 1 (vector (_"CheckListBox wxLB_EXTENDED")) wxLB_EXTENDED))
        ;;; end wxGlade
        )

(defmethod set-properties ((obj Frame194))
        ;;; begin wxGlade: Frame194.__set_properties
        (wxFrame_SetTitle (slot-top-window obj) (_"frame_1"))
        (wxListBox_SetSelection (slot-list-box-single obj) 0)
        (wxListBox_SetSelection (slot-list-box-multiple obj) 0)
        (wxListBox_SetSelection (slot-list-box-extended obj) 0)
        (wxCheckListBox_SetSelection (slot-check-list-box-single obj) 0)
        (wxCheckListBox_SetSelection (slot-check-list-box-multiple obj) 0)
        (wxCheckListBox_SetSelection (slot-check-list-box-extended obj) 0)
        ;;; end wxGlade
        )

(defmethod do-layout ((obj Frame194))
        ;;; begin wxGlade: Frame194.__do_layout
        (setf (slot-sizer-1 obj) (wxGridSizer_Create 2 3 0 0))
        (wxSizer_AddWindow (slot-sizer-1 obj) (slot-list-box-single obj) 1 (logior wxALL wxEXPAND) 5 nil)
        (wxSizer_AddWindow (slot-sizer-1 obj) (slot-list-box-multiple obj) 1 (logior wxALL wxEXPAND) 5 nil)
        (wxSizer_AddWindow (slot-sizer-1 obj) (slot-list-box-extended obj) 1 (logior wxALL wxEXPAND) 5 nil)
        (wxSizer_AddWindow (slot-sizer-1 obj) (slot-check-list-box-single obj) 1 (logior wxALL wxEXPAND) 5 nil)
        (wxSizer_AddWindow (slot-sizer-1 obj) (slot-check-list-box-multiple obj) 1 (logior wxALL wxEXPAND) 5 nil)
        (wxSizer_AddWindow (slot-sizer-1 obj) (slot-check-list-box-extended obj) 1 (logior wxALL wxEXPAND) 5 nil)
        (wxWindow_SetSizer (slot-frame obj) (slot-sizer-1 obj))
        (wxFrame_layout (slot-Bug194-Frame self))
        ;;; end wxGlade
        )

;;; end of class Frame194


(defun init-func (fun data evt)
        (let ((Bug194-Frame (make-Frame194)))
        (ELJApp_SetTopWindow (slot-top-window Bug194-Frame))
        (wxWindow_Show (slot-top-window Bug194-Frame))))
;;; end of class MyApp

    (setf (textdomain) "app") ;; replace with the appropriate catalog name
    (defun _ (msgid) (gettext msgid "app"))


(unwind-protect
    (Eljapp_initializeC (wxclosure_Create #'init-func nil) 0 nil)
    (ffi:close-foreign-library "../miscellaneous/wxc-msw2.6.2.dll"))
