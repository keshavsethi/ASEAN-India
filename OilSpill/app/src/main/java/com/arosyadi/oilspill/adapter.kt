package com.arosyadi.oilspill

import android.content.Context
import android.content.Intent
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.firebase.ui.database.FirebaseRecyclerAdapter
import com.firebase.ui.database.FirebaseRecyclerOptions
import kotlinx.android.synthetic.main.item_vessel.view.*


class vesselAdapter(
    val context : Context, val data: MutableList<Vessel>?
) : RecyclerView.Adapter<vesselAdapter.vesselViewholder>() {
    // Function to bind the view in Card view(here
    // "person.xml") iwth data in
    // model class(here "person.class")
    override fun onBindViewHolder(
        holder: vesselViewholder,
        position: Int
    ) {
        holder.bindView(data?.get(position))
    }

    // Function to tell the class about the Card view (here
    // "person.xml")in
    // which the data will be shown
    override fun onCreateViewHolder(
        parent: ViewGroup,
        viewType: Int
    ): vesselViewholder {
        val view: View = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_vessel, parent, false)
        return vesselViewholder(view)
    }


    inner class vesselViewholder(itemView: View) :
        RecyclerView.ViewHolder(itemView) {

        fun bindView(vessel : Vessel?) {
            with(itemView) {
                tv_vessel.text = "Name : " + vessel?.name
                tv_timestamp.text = "Date: " + vessel?.timestamp
                tv_mmsi.text = "MMSI : " + vessel?.mmsi
                tv_lat.text = "Lat : " + vessel?.location?.lat.toString()
                tv_long.text = "Long : " + vessel?.location?.long.toString()
                tv_course.text = "Course : " + vessel?.course?.toString()
                tv_speed.text = "Speed : " + vessel?.speed?.toString()
                tv_rot.text = "Rot : " + vessel?.rot?.toString()

                btn_maps.setOnClickListener {
                    val intent = Intent(context, MapsActivity::class.java)
                    intent.putExtra("lat", vessel?.location?.lat ?: 0.0)
                    intent.putExtra("long", vessel?.location?.long ?: 0.0)
                    intent.putExtra("name", vessel?.name ?: "BLANK")
                    context.startActivity(intent)
                }
            }
        }
    }

    override fun getItemCount(): Int = data?.size ?: 0
}