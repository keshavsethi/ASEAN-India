package com.arosyadi.oilspill

import android.content.Context
import android.graphics.*
import android.os.AsyncTask
import android.os.Bundle
import android.os.PersistableBundle
import android.view.LayoutInflater
import android.view.View
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.mapbox.geojson.Feature
import com.mapbox.geojson.FeatureCollection
import com.mapbox.geojson.Point
import com.mapbox.mapboxsdk.Mapbox
import com.mapbox.mapboxsdk.annotations.BubbleLayout
import com.mapbox.mapboxsdk.geometry.LatLng
import com.mapbox.mapboxsdk.maps.MapView
import com.mapbox.mapboxsdk.maps.MapboxMap
import com.mapbox.mapboxsdk.maps.OnMapReadyCallback
import com.mapbox.mapboxsdk.maps.Style
import com.mapbox.mapboxsdk.style.expressions.Expression.*
import com.mapbox.mapboxsdk.style.layers.Property.ICON_ANCHOR_BOTTOM
import com.mapbox.mapboxsdk.style.layers.PropertyFactory.*
import com.mapbox.mapboxsdk.style.layers.SymbolLayer
import com.mapbox.mapboxsdk.style.sources.GeoJsonSource
import java.io.InputStream
import java.lang.ref.WeakReference
import java.nio.charset.Charset


class InfoWindowSymbolLayerActivity : AppCompatActivity(), OnMapReadyCallback, MapboxMap.OnMapClickListener {


    private var mapView: MapView? = null
    private var mapboxMap: MapboxMap? = null
    private var source: GeoJsonSource? = null
    private var featureCollection: FeatureCollection? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

// Mapbox access token is configured here. This needs to be called either in your application
// object or in the same activity which contains the mapview.
        Mapbox.getInstance(this, getString(R.string.mapbox_access_token))

// This contains the MapView in XML and needs to be called after the access token is configured.
        setContentView(R.layout.activity_maps)

// Initialize the map view
        mapView = findViewById<MapView?>(R.id.mapView)
        mapView!!.onCreate(savedInstanceState)
        mapView!!.getMapAsync(this)
    }

    override fun onMapReady(mapboxMap: MapboxMap) {
        this.mapboxMap = mapboxMap
        mapboxMap.setStyle(Style.MAPBOX_STREETS) {
            LoadGeoJsonDataTask(this@InfoWindowSymbolLayerActivity).execute()
            mapboxMap.addOnMapClickListener(this@InfoWindowSymbolLayerActivity)
        }
    }

    override fun onMapClick(point: LatLng): Boolean {
        return handleClickIcon(mapboxMap!!.projection.toScreenLocation(point))
    }

    /**
     * Sets up all of the sources and layers needed for this example
     *
     * @param collection the FeatureCollection to set equal to the globally-declared FeatureCollection
     */
    fun setUpData(collection: FeatureCollection?) {
        featureCollection = collection
        if (mapboxMap != null) {
            mapboxMap!!.getStyle { style: Style? ->
                setupSource(style!!)
                setUpImage(style)
                setUpMarkerLayer(style)
                setUpInfoWindowLayer(style)
            }
        }
    }

    /**
     * Adds the GeoJSON source to the map
     */
    private fun setupSource(loadedStyle: Style) {
        source = GeoJsonSource(GEOJSON_SOURCE_ID, featureCollection)
        loadedStyle.addSource(source!!)
    }

    /**
     * Adds the marker image to the map for use as a SymbolLayer icon
     */
    private fun setUpImage(loadedStyle: Style) {
        loadedStyle.addImage(
            MARKER_IMAGE_ID!!, BitmapFactory.decodeResource(
                this.resources, R.drawable.mapbox_marker_icon_default
            )
        )
    }

    /**
     * Updates the display of data on the map after the FeatureCollection has been modified
     */
    private fun refreshSource() {
        if (source != null && featureCollection != null) {
            source!!.setGeoJson(featureCollection)
        }
    }

    /**
     * Setup a layer with maki icons, eg. west coast city.
     */
    private fun setUpMarkerLayer(loadedStyle: Style) {
        loadedStyle.addLayer(
            SymbolLayer(MARKER_LAYER_ID, GEOJSON_SOURCE_ID)
                .withProperties(
                    iconImage(MARKER_IMAGE_ID),
                    iconAllowOverlap(true),
                    iconOffset(arrayOf<Float?>(0f, -8f))
                )
        )
    }

    /**
     * Setup a layer with Android SDK call-outs
     *
     *
     * name of the feature is used as key for the iconImage
     *
     */
    private fun setUpInfoWindowLayer(loadedStyle: Style) {
        loadedStyle.addLayer(
            SymbolLayer(CALLOUT_LAYER_ID, GEOJSON_SOURCE_ID)
                .withProperties( /* show image with id title based on the value of the name feature property */
                    iconImage("{name}"),  /* set anchor of icon to bottom-left */
                    iconAnchor(ICON_ANCHOR_BOTTOM),  /* all info window and marker image to appear at the same time*/
                    iconAllowOverlap(true),  /* offset the info window to be above the marker */
                    iconOffset(arrayOf<Float?>(-2f, -28f))
                ) /* add a filter to show only when selected feature property is true */
                .withFilter(eq(get(PROPERTY_SELECTED), literal(true)))
        )
    }

    /**
     * This method handles click events for SymbolLayer symbols.
     *
     *
     * When a SymbolLayer icon is clicked, we moved that feature to the selected state.
     *
     *
     * @param screenPoint the point on screen clicked
     */
    private fun handleClickIcon(screenPoint: PointF?): Boolean {
        val features: MutableList<Feature?> =
            mapboxMap!!.queryRenderedFeatures(screenPoint!!, MARKER_LAYER_ID)
        return if (features.isNotEmpty()) {
            val name: String = features[0]?.getStringProperty(PROPERTY_NAME) ?: "selected"
            val featureList: MutableList<Feature?>? =
                featureCollection!!.features()
            if (featureList != null) {
                for (i in featureList.indices) {
                    if (featureList[i]?.getStringProperty(PROPERTY_NAME).equals(name)) {
                        if (featureSelectStatus(i)) {
                            setFeatureSelectState(featureList[i], false)
                        } else {
                            setSelected(i)
                        }
                    }
                }
            }
            true
        } else {
            false
        }
    }

    /**
     * Set a feature selected state.
     *
     * @param index the index of selected feature
     */
    private fun setSelected(index: Int) {
        if (featureCollection!!.features() != null) {
            val feature: Feature? = featureCollection!!.features()!![index]
            setFeatureSelectState(feature, true)
            refreshSource()
        }
    }

    /**
     * Selects the state of a feature
     *
     * @param feature the feature to be selected.
     */
    private fun setFeatureSelectState(
        feature: Feature?,
        selectedState: Boolean
    ) {
        if (feature?.properties() != null) {
            feature.properties()!!.addProperty(PROPERTY_SELECTED, selectedState)
            refreshSource()
        }
    }

    /**
     * Checks whether a Feature's boolean "selected" property is true or false
     *
     * @param index the specific Feature's index position in the FeatureCollection's list of Features.
     * @return true if "selected" is true. False if the boolean property is false.
     */
    private fun featureSelectStatus(index: Int): Boolean {
        return if (featureCollection == null) {
            false
        } else featureCollection!!.features()!![index].getBooleanProperty(PROPERTY_SELECTED)
    }

    /**
     * Invoked when the bitmaps have been generated from a view.
     */
    fun setImageGenResults(imageMap: HashMap<String?, Bitmap?>?) {
        if (mapboxMap != null) {
            mapboxMap!!.getStyle { style: Style? ->
                // calling addImages is faster as separate addImage calls for each bitmap.
                style!!.addImages(imageMap!!)
            }
        }
    }

    /**
     * AsyncTask to load data from the assets folder.
     */
    private class LoadGeoJsonDataTask internal constructor(activity: InfoWindowSymbolLayerActivity?) :
        AsyncTask<Void?, Void?, FeatureCollection?>() {
        private val activityRef: WeakReference<InfoWindowSymbolLayerActivity?>?
        override fun doInBackground(vararg params: Void?): FeatureCollection? {
            val activity: InfoWindowSymbolLayerActivity = activityRef?.get() ?: return null

            val symbolLayerIconFeatureList: MutableList<Feature> = ArrayList()
            symbolLayerIconFeatureList.add(
                Feature.fromGeometry(
                    Point.fromLngLat(0.0, 0.0)
                )
            )

//            val geoJson = loadGeoJsonFromAsset(
//                activity,
//                "us_west_coast.geojson"
//            )
            return FeatureCollection.fromFeatures(symbolLayerIconFeatureList)
        }

        override fun onPostExecute(featureCollection: FeatureCollection?) {
            super.onPostExecute(featureCollection)
            val activity: InfoWindowSymbolLayerActivity? = activityRef?.get()
            if (featureCollection == null || activity == null) {
                return
            }

// This example runs on the premise that each GeoJSON Feature has a "selected" property,
// with a boolean value. If your data's Features don't have this boolean property,
// add it to the FeatureCollection 's features with the following code:
            for (singleFeature in featureCollection.features()!!) {
                singleFeature.addBooleanProperty(PROPERTY_SELECTED, false)
            }
            activity.setUpData(featureCollection)
            GenerateViewIconTask(activity).execute(featureCollection)
        }

        companion object {
            fun loadGeoJsonFromAsset(context: Context?, filename: String?): String? {
                return try {
                    // Load GeoJSON file from local asset folder
                    val `is`: InputStream = filename?.let { context?.assets?.open(it) }!!
                    val size: Int = `is`.available()
                    val buffer = ByteArray(size)
                    `is`.read(buffer)
                    `is`.close()
                    String(buffer, Charset.forName("UTF-8"))
                } catch (exception: Exception) {
                    throw RuntimeException(exception)
                }
            }
        }

        init {
            activityRef = WeakReference(activity)
        }
    }

    /**
     * AsyncTask to generate Bitmap from Views to be used as iconImage in a SymbolLayer.
     *
     *
     * Call be optionally be called to update the underlying data source after execution.
     *
     *
     *
     * Generating Views on background thread since we are not going to be adding them to the view hierarchy.
     *
     */
    private class GenerateViewIconTask @JvmOverloads internal constructor(
        activity: InfoWindowSymbolLayerActivity?,
        refreshSource: Boolean = false
    ) :
        AsyncTask<FeatureCollection?, Void?, HashMap<String?, Bitmap?>?>() {
        private val viewMap: HashMap<String?, View?>? = HashMap()
        private val activityRef: WeakReference<InfoWindowSymbolLayerActivity?>?
        private val refreshSource: Boolean
        override fun doInBackground(vararg params: FeatureCollection?): HashMap<String?, Bitmap?>? {
            val activity: InfoWindowSymbolLayerActivity? = activityRef?.get()
            return if (activity != null) {
                val imagesMap: HashMap<String?, Bitmap?> = HashMap()
                val inflater = LayoutInflater.from(activity)
                val featureCollection = params[0]
                for (feature in featureCollection!!.features()!!) {
                    val bubbleLayout = inflater!!.inflate(
                        R.layout.symbol_layer_info_window_layout_callout,
                        null
                    ) as BubbleLayout
                    val name = feature.getStringProperty(PROPERTY_NAME)
                    val titleTextView =
                        bubbleLayout.findViewById<TextView?>(R.id.info_window_title)
                    titleTextView!!.text = name
                    val style = feature.getStringProperty(PROPERTY_CAPITAL)
                    val descriptionTextView =
                        bubbleLayout.findViewById<TextView?>(R.id.info_window_description)
                    descriptionTextView!!.text = String.format(
                        activity.getString(R.string.capital),
                        style
                    )
                    val measureSpec: Int =
                        View.MeasureSpec.makeMeasureSpec(0, View.MeasureSpec.UNSPECIFIED)
                    bubbleLayout.measure(measureSpec, measureSpec)
                    val measuredWidth = bubbleLayout.measuredWidth.toFloat()
                    bubbleLayout.arrowPosition = measuredWidth / 2 - 5
                    val bitmap = SymbolGenerator.generate(bubbleLayout)
                    imagesMap[name] = bitmap
                    viewMap!![name] = bubbleLayout
                }
                imagesMap
            } else {
                null
            }
        }

        override fun onPostExecute(bitmapHashMap: HashMap<String?, Bitmap?>?) {
            super.onPostExecute(bitmapHashMap)
            val activity: InfoWindowSymbolLayerActivity? = activityRef?.get()
            if (activity != null && bitmapHashMap != null) {
                activity.setImageGenResults(bitmapHashMap)
                if (refreshSource) {
                    activity.refreshSource()
                }
            }
            Toast.makeText(activity, R.string.tap_on_marker_instruction, Toast.LENGTH_SHORT).show()
        }

        init {
            activityRef = WeakReference(activity)
            this.refreshSource = refreshSource
        }
    }

    /**
     * Utility class to generate Bitmaps for Symbol.
     */
    private object SymbolGenerator {
        /**
         * Generate a Bitmap from an Android SDK View.
         *
         * @param view the View to be drawn to a Bitmap
         * @return the generated bitmap
         */
        fun generate(view: View): Bitmap? {
            val measureSpec: Int = View.MeasureSpec.makeMeasureSpec(0, View.MeasureSpec.UNSPECIFIED)
            view.measure(measureSpec, measureSpec)
            val measuredWidth: Int = view.getMeasuredWidth()
            val measuredHeight: Int = view.getMeasuredHeight()
            view.layout(0, 0, measuredWidth, measuredHeight)
            val bitmap =
                Bitmap.createBitmap(measuredWidth, measuredHeight, Bitmap.Config.ARGB_8888)
            bitmap!!.eraseColor(Color.TRANSPARENT)
            val canvas = Canvas(bitmap)
            view.draw(canvas)
            return bitmap
        }
    }

    override fun onStart() {
        super.onStart()
        mapView!!.onStart()
    }

    override fun onResume() {
        super.onResume()
        mapView!!.onResume()
    }

    override fun onPause() {
        super.onPause()
        mapView!!.onPause()
    }

    override fun onStop() {
        super.onStop()
        mapView!!.onStop()
    }

    override fun onSaveInstanceState(outState: Bundle, outPersistentState: PersistableBundle) {
        super.onSaveInstanceState(outState, outPersistentState)
        mapView!!.onSaveInstanceState(outState)
    }

    override fun onLowMemory() {
        super.onLowMemory()
        mapView!!.onLowMemory()
    }

    override fun onDestroy() {
        super.onDestroy()
        if (mapboxMap != null) {
            mapboxMap!!.removeOnMapClickListener(this)
        }
        mapView!!.onDestroy()
    }

    companion object {
        const val GEOJSON_SOURCE_ID = "GEOJSON_SOURCE_ID"
        const val MARKER_IMAGE_ID = "MARKER_IMAGE_ID"
        const val MARKER_LAYER_ID = "MARKER_LAYER_ID"
        const val CALLOUT_LAYER_ID = "CALLOUT_LAYER_ID"
        const val PROPERTY_SELECTED = "selected"
        const val PROPERTY_NAME = "name"
        const val PROPERTY_CAPITAL = "capital"
    }
}