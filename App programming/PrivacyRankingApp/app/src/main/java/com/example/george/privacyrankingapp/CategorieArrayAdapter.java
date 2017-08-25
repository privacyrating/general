package com.example.george.privacyrankingapp;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.AsyncTask;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.ImageView;
import android.widget.TextView;

import java.io.InputStream;
import java.util.ArrayList;

/**
 * Adapter Klasse, baut App Kategorie auf.
 */
public class CategorieArrayAdapter extends ArrayAdapter<AppContact>{

    public ImageView ivIcon = null;

    /**
     * Constructor zu Kategorie Adapter
     * @param objects Liste alle App zugehoerige Kategorie
     */
    public CategorieArrayAdapter(Context context, int resource, ArrayList<AppContact> objects) {
        super(context, 0, objects);
    }


    /**
     * Methode die das View auffuellt
     *
     * @param position Element position auf dem zugegriffen wird
     * @param convertView View die aufgebaut wird
     * @param parent Verfahren des Views
     * @return
     */
    @Override
    public View getView(int position, View convertView, ViewGroup parent) {
        // Get the data item for this position
        AppContact appContact = getItem(position);

        // Check if an existing view is being reused, otherwise inflate the view
        if (convertView == null) {
            convertView = LayoutInflater.from(getContext()).inflate(R.layout.list_item_cat_chekbox, parent, false);
        }

        // Lookup view for data population
        TextView tvTitle = (TextView) convertView.findViewById(R.id.appTitle);
        TextView tvPerm = (TextView) convertView.findViewById(R.id.appPerm);


        // Populate the data into the template view using the data object
        tvTitle.setText(appContact.title);
        tvPerm.setText(appContact.permissions);

        float hue = Float.parseFloat(appContact.similarity);
        float newHue = (hue * 120) / 100;
        float[] hsv = {newHue, 1, 1};

        ImageView myView  = (ImageView) convertView.findViewById(R.id.myView);
        DrawView drawView = new DrawView(myView, hsv);
        drawView.onDraw();

        ivIcon = (ImageView) convertView.findViewById(R.id.myViewIcon);

        DownloadExampleActivity loadBitmap = new DownloadExampleActivity(appContact.icon, ivIcon);
        loadBitmap.downloadPicture();

        return convertView;
    }
}
