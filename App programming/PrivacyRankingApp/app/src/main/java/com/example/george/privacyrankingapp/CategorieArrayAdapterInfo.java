package com.example.george.privacyrankingapp;

import android.content.Context;
import android.graphics.Color;
import android.graphics.drawable.GradientDrawable;
import android.text.SpannableString;
import android.text.SpannableStringBuilder;
import android.text.style.ForegroundColorSpan;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.RatingBar;
import android.widget.TextView;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

/**
 * Adapter Klasse, baut App Vergleich Kategorie auf.
 */
class CategorieArrayAdapterInfo extends ArrayAdapter<AppContact> {

    /**
     * Constructor zu Kategorie Adapter
     * @param objects liste alle App zugehörige Kategorie
     */
    public CategorieArrayAdapterInfo(Context context, int resource, ArrayList<AppContact> objects) {
        super(context, 0, objects);
    }

    /**
     * Methode die das View auffühlt
     *
     * @param position Ellement position auf dem zugegriefen wird
     * @param convertView View die aufgebaut wird
     * @param parent Vorvaren des Views
     * @return
     */
    @Override
    public View getView(int position, View convertView, ViewGroup parent) {
        // Get the data item for this position
        AppContact appContact = getItem(position);

        // Check if an existing view is being reused, otherwise inflate the view
        if (convertView == null) {
            convertView = LayoutInflater.from(getContext()).inflate(R.layout.list_item2, parent, false);
        }

        // Lookup view for data population
        TextView tvTitle = (TextView) convertView.findViewById(R.id.title);
        TextView tvTitle_en = (TextView) convertView.findViewById(R.id.title_en);
        TextView tvPermList = (TextView) convertView.findViewById(R.id.name);
        TextView tvDescr = (TextView) convertView.findViewById(R.id.description);
        RatingBar tvRating = (RatingBar) convertView.findViewById(R.id.playstorRating);
        TextView tvPrivaRat = (TextView) convertView.findViewById(R.id.privacyRating);
        TextView tvMinDown = (TextView) convertView.findViewById(R.id.min_downloads);
        TextView tvCost = (TextView) convertView.findViewById(R.id.cost);
        TextView tvChanglog = (TextView) convertView.findViewById(R.id.changelog);
        TextView tvLink = (TextView) convertView.findViewById(R.id.link);

        // Populate the data into the template view using the data object
        tvTitle.setText(appContact.title);
        tvTitle_en.setText(appContact.title_en);
        tvDescr.setText(appContact.description);
        tvMinDown.setText(appContact.min_downloads);
        tvCost.setText(appContact.cost);
        tvChanglog.setText(appContact.changelog);
        tvLink.setText(appContact.link);

        // Permission in verschieden Farben darstehlen
        HashMap<String, String> permList = appContact.permissionsList;
        SpannableStringBuilder builder = new SpannableStringBuilder();
        int size = permList.size();

        for (Map.Entry<String, String> entry : permList.entrySet()) {
            SpannableString str = new SpannableString(entry.getKey());
            float hue = Float.parseFloat(entry.getValue());
            float newHue = 100 - hue * 100;
            float[] hsv = {newHue, 1, 1};

            str.setSpan(new ForegroundColorSpan(Color.HSVToColor(hsv)), 0, str.length(), 0);
            builder.append(str);

            SpannableString str1;
            if (size > 1) {
                str1 = new SpannableString(", ");
            } else {
                str1 = new SpannableString(".");
            }
            builder.append(str1);

            size--;
        }
        tvPermList.setText( builder, TextView.BufferType.SPANNABLE);

        //RatingBar
        int rating = Integer.valueOf(appContact.rating);
        Log.d("MyTest", appContact.rating);
        tvRating.setRating(rating);

        float hue = Float.parseFloat(appContact.similarity);
        float newHue = (hue * 120) / 100;
        float[] hsv = {newHue, 1, 1};

        GradientDrawable gradient = new GradientDrawable(GradientDrawable.Orientation.LEFT_RIGHT, new int[]{Color.GREEN, Color.HSVToColor(hsv)});
        gradient.setShape(GradientDrawable.RECTANGLE);
        tvPrivaRat.setBackgroundDrawable(gradient);

        // Return the completed view to render on screen
        return convertView;
    }
}