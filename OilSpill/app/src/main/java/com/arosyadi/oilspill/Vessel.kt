package com.arosyadi.oilspill

import android.os.Parcelable
import com.google.gson.annotations.SerializedName
import kotlinx.android.parcel.Parcelize

@Parcelize
data class VesselById(
    var vesselData: Vessel?
) : Parcelable {
    constructor(): this(
        vesselData = null
    )
}

@Parcelize
data class Vessel(
    var course: Int?,
    var location: Location?,
    var rot: Int?,
    var speed: Int?,
    var mmsi: String?,
    var name: String?,
    var timestamp: String?
) : Parcelable {
    constructor() : this(
        course = null,
        location = null,
        rot = null,
        speed = null,
        mmsi = null,
        name = null,
        timestamp = null
    )
}

@Parcelize
data class Location(
    var lat: Double?,
    var long: Double?
) : Parcelable {
    constructor(): this(
        lat = null,
        long = null
    )
}

