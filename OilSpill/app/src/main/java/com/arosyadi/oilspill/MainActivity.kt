package com.arosyadi.oilspill

import android.app.Activity
import android.app.NotificationChannel
import android.app.NotificationManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.util.Log
import android.webkit.ValueCallback
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import androidx.recyclerview.widget.LinearLayoutManager
import com.firebase.ui.database.FirebaseRecyclerOptions
import com.google.firebase.database.*
import kotlinx.android.synthetic.main.activity_dashboard.*

class MainActivity : AppCompatActivity() {

    val TAG = "hellow web view"

    var uploadMessage: ValueCallback<Array<Uri>>? = null
    private val FILECHOOSER_RESULTCODE = 1
    val REQUEST_SELECT_FILE = 100

    var id = 0

    private lateinit var adapterVessel : vesselAdapter

    private var vesselData : MutableList<Vessel> ? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_dashboard)

        val db = FirebaseDatabase.getInstance("https://oilspill-8c6be-default-rtdb.firebaseio.com/")
        val reference = db.reference.child("vessel")

        reference.addValueEventListener(object : ValueEventListener {
            override fun onCancelled(p0: DatabaseError) {

            }

            override fun onDataChange(dataSnapshot: DataSnapshot) {
                val dataAdapter = mutableListOf<Vessel>()
                if (dataSnapshot.exists()) {
                    id = dataSnapshot.childrenCount.toInt()

                    for (h in dataSnapshot.children) {

                        val data = h.getValue(Vessel::class.java)
                        if (data != null) {
                            dataAdapter.add(data)
                        }
                    }
                    with(rv_vessel) {
                        layoutManager = LinearLayoutManager(context)
                    }
                    val adapter = vesselAdapter(baseContext, dataAdapter)
                    rv_vessel?.adapter = adapter

                }
            }

        })

        reference.addChildEventListener(object: ChildEventListener {
            override fun onCancelled(p0: DatabaseError) {
            }

            override fun onChildMoved(p0: DataSnapshot, p1: String?) {
            }

            override fun onChildChanged(p0: DataSnapshot, p1: String?) {
            }

            override fun onChildAdded(p0: DataSnapshot, p1: String?) {
                notification()
            }

            override fun onChildRemoved(p0: DataSnapshot) {
            }
        })
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
            .setSmallIcon(R.drawable.ic_oil_tanker)
            .setAutoCancel(true)
            .setContentText("There is an anomaly for some vessel, check it immediately!")

        val managerCompat = NotificationManagerCompat.from(this)
        managerCompat.notify(999, builder.build())
    }
}

