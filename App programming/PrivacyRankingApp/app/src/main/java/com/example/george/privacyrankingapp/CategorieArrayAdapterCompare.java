package com.example.george.privacyrankingapp;

import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.CheckBox;
import android.widget.ImageView;
import android.widget.TextView;

import java.util.ArrayList;

/**
 * Adapter Klasser, bauet App Vergleich Kategori auf.
 */
public class CategorieArrayAdapterCompare extends ArrayAdapter<AppContact>{

    private DrawView drawView;
    public ImageView ivIcon = null;

    /**
     * Constructor zu Kategorie Adapter
     * @param objects liste alle App zugehörige Kategorie
     */
    public CategorieArrayAdapterCompare(Context context, int resource, ArrayList<AppContact> objects) {
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
            convertView = LayoutInflater.from(getContext()).inflate(R.layout.list_item_cat, parent, false);
        }

        // Lookup view for data population
        TextView tvTitle = (TextView) convertView.findViewById(R.id.appTitle);
        TextView tvPerm = (TextView) convertView.findViewById(R.id.appPerm);
        CheckBox checkBox = (CheckBox) convertView.findViewById(R.id.Comp_id);

        // Populate the data into the template view using the data object
        tvTitle.setText(appContact.title);
        tvPerm.setText(appContact.permissions);
        checkBox.setChecked(appContact.checkboxChecked);
        checkBox.setTag(appContact);

        float hue = Float.parseFloat(appContact.similarity);
        float newHue = (hue * 120) / 100;
        float[] hsv = {newHue, 1, 1};

        ImageView myView = (ImageView) convertView.findViewById(R.id.myView);
        drawView = new DrawView(myView, hsv);
        drawView.onDraw();

        ivIcon = (ImageView) convertView.findViewById(R.id.myViewIcon);
        DownloadExampleActivity loadBitmap = new DownloadExampleActivity(appContact.icon, ivIcon);
        loadBitmap.downloadPicture();

        // Return the completed view to render on screen
        return convertView;
    }
}