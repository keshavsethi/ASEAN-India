package com.arosyadi.oilspill

import android.app.DownloadManager
import android.app.DownloadManager.*
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.Environment
import android.util.AttributeSet
import android.util.Log
import android.view.KeyEvent
import android.view.View
import android.webkit.*
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import androidx.core.content.ContentProviderCompat.requireContext
import com.google.firebase.database.*
import kotlinx.android.synthetic.main.activity_main.*

class MainActivity : AppCompatActivity() {

    val TAG = "hellow web view"

    var uploadMessage: ValueCallback<Array<Uri>>? = null
    private val FILECHOOSER_RESULTCODE = 1
    val REQUEST_SELECT_FILE = 100

    var id = 0

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val reference = FirebaseDatabase.getInstance("https://oilspill-8c6be-default-rtdb.firebaseio.com/").reference.child("Vessel")

        reference.addValueEventListener(object : ValueEventListener {
            override fun onCancelled(p0: DatabaseError) {
                TODO("Not yet implemented")
            }

            override fun onDataChange(dataSnapshot: DataSnapshot) {
                if (dataSnapshot.exists()) {
                    id = dataSnapshot.childrenCount.toInt()
                }
            }

        })

        reference.addChildEventListener(object: ChildEventListener {
            override fun onCancelled(p0: DatabaseError) {
                TODO("Not yet implemented")
            }

            override fun onChildMoved(p0: DataSnapshot, p1: String?) {
                TODO("Not yet implemented")
            }

            override fun onChildChanged(p0: DataSnapshot, p1: String?) {
                TODO("Not yet implemented")
            }

            override fun onChildAdded(p0: DataSnapshot, p1: String?) {
                notification()
            }

            override fun onChildRemoved(p0: DataSnapshot) {
                TODO("Not yet implemented")
            }
        })

//        with(wv_oil) {
//            if (savedInstanceState == null) {
//                savedInstanceState?.let { restoreState(it) }
//                loadUrl("https://share.streamlit.io/keshavsethi/streamlit/main.py")
//                settings.javaScriptEnabled = true
//                settings.builtInZoomControls = true
//                settings.displayZoomControls = true
//                settings.allowFileAccess = true
//                settings.allowFileAccessFromFileURLs = true
//
//                wv_oil.setWebChromeClient(object:WebChromeClient() {
//                    override fun onShowFileChooser(webView:WebView, filePathCallback:ValueCallback<Array<Uri>>, fileChooserParams:FileChooserParams):Boolean {
//                        var mFilePathCallback = filePathCallback
//                        val intent = Intent(Intent.ACTION_GET_CONTENT)
//                        intent.setType("*/*")
//                        val PICKFILE_REQUEST_CODE = 100
//                        startActivityForResult(intent, PICKFILE_REQUEST_CODE)
//                        return true
//                    }
//                })
//
//                fun onActivityResult(requestCode: Int, resultCode: Int,
//                                     intent: Intent,
//                                     mFilePathCallback: Any): Boolean {
//                    var PICKFILE_REQUEST_CODE = null
//                    if (requestCode == PICKFILE_REQUEST_CODE)
//                    {
//                        val result = if (intent == null || resultCode != RESULT_OK)
//                            null
//                        else
//                            intent.getData()
//                        val resultsArray = arrayOfNulls<Uri>(1)
//                        resultsArray[0] = result
//                        mFilePathCallback.onReceiveValue(resultsArray)
//
//                    }
//                    return true
//                }
//
//
//
//                wv_oil.setDownloadListener(object : DownloadListener {
//                    override fun onDownloadStart(url: String, userAgent: String,
//                                                 contentDisposition: String, mimetype: String,
//                                                 contentLength: Long) {
//                        val request = Request(Uri.parse(url))
//                        request.allowScanningByMediaScanner()
//
//                        request.setAllowedNetworkTypes(Request.NETWORK_WIFI or Request.NETWORK_MOBILE)
//                        request.setNotificationVisibility(Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED) //Notify client once download is completed!
//                        request.setDestinationInExternalPublicDir(Environment.DIRECTORY_DOWNLOADS, mimetype)
//                        val webview = getSystemService(DOWNLOAD_SERVICE) as DownloadManager
//                        webview.enqueue(request)
//                        Toast.makeText(getApplicationContext(), "Downloading File", Toast.LENGTH_LONG).show()
//                    }
//                })
//
//                class webviewclient : WebViewClient() {
//                    override fun shouldOverrideUrlLoading(view: WebView?, request: WebResourceRequest?): Boolean {
//                        wv_oil.loadUrl("http://google.com")
//                        return true
//                    }
//                }
////                searchbtn.setOnClickListener({ (webview.loadUrl("https://www.google.com")) })
////
////                btn1.setOnClickListener({ (webview.goBack()) })
////
////                btn3.setOnClickListener({ (webview.goForward()) })
//            }
//        }
//        settingWebview()
    }

//    fun settingWebview() {
//        wv_oil.webChromeClient = object : WebChromeClient() {
//            override fun onShowFileChooser(
//                webView: WebView,
//                filePathCallback: ValueCallback<Array<Uri>>,
//                fileChooserParams: FileChooserParams
//            ): Boolean {
//                var mFilePathCallback = filePathCallback
//                val intent = Intent(Intent.ACTION_GET_CONTENT)
//                intent.type = "*/*"
//                val PICKFILE_REQUEST_CODE = 100
//                startActivityForResult(intent, PICKFILE_REQUEST_CODE)
//                return true
//            }
//        }
//    }
//
//    fun onActivityResult(
//        requestCode: Int, resultCode: Int,
//        intent: Intent,
//        mFilePathCallback: Any
//    ): Boolean {
//        var PICKFILE_REQUEST_CODE = null
//        if (requestCode == PICKFILE_REQUEST_CODE) {
//            val result = if (intent == null || resultCode != RESULT_OK)
//                null
//            else
//                intent.getData()
//            val resultsArray = arrayOfNulls<Uri>(1)
//            resultsArray[0] = result
//            mFilePathCallback.onReceiveValue(resultsArray)
//
//        }
//        return true
//    }
//
//    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
//
//        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
//            if (requestCode == REQUEST_SELECT_FILE) {
//                if (uploadMessage != null) {
//                    uploadMessage?.onReceiveValue(
//                        WebChromeClient.FileChooserParams.parseResult(
//                            resultCode,
//                            data
//                        )
//                    )
//                    uploadMessage = null
//                }
//            }
//        } else if (requestCode == FILECHOOSER_RESULTCODE) {
//            if (mUploadMessage != null) {
//                var result = data?.data
//                mUploadMessage?.onReceiveValue(result)
//                mUploadMessage = null
//            }
//        } else {
//            Toast.makeText(
//                requireContext(),
//                "Failed to open file uploader, please check app permissions.",
//                Toast.LENGTH_LONG
//            ).show()
//            super.onActivityResult(requestCode, resultCode, data)
//        }
//
//
//    }

    override fun onKeyDown(keyCode: Int, event: KeyEvent): Boolean {
        if (keyCode == KeyEvent.KEYCODE_BACK && wv_oil.canGoBack()) {
            wv_oil.goBack()
            return true
        }
        return super.onKeyDown(keyCode, event)
    }


    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        wv_oil.saveState(outState)
        Log.i(TAG, "onSaveInstanceState")
    }

    override fun onRestoreInstanceState(savedInstanceState: Bundle) {
        super.onRestoreInstanceState(savedInstanceState)
        wv_oil.restoreState(savedInstanceState)
        Log.i(TAG, "onRestoreInstanceState")
    }


    private fun Any.onReceiveValue(resultsArray: Array<Uri?>) {}

    private fun notification() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel("n", "n", NotificationManager.IMPORTANCE_DEFAULT)
            val manager = getSystemService(NotificationManager::class.java)

            manager.createNotificationChannel(channel)

        }

        val builder = NotificationCompat.Builder(this, "n")
            .setContentText("Oil Spill")
            .setSmallIcon(R.drawable.ic_baseline_notifications_24)
            .setAutoCancel(true)
            .setContentText("There is an anomaly for some vessels, check it immediately!")

        val managerCompat = NotificationManagerCompat.from(this)
        managerCompat.notify(999, builder.build())
    }
}