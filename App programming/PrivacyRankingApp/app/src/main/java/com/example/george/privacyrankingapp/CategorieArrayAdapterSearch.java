package com.example.george.privacyrankingapp;


import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.ImageView;
import android.widget.TextView;

import java.util.ArrayList;

/**
 * Adapter Klasser, baut App Suche Kategorie auf.
 */
public class CategorieArrayAdapterSearch extends ArrayAdapter<AppContact>{

    public ImageView ivIcon = null;
    private Context context;
    private ArrayList<AppContact> appcontactList;

    /**
     * Constructor zu Kategorie Adapter
     * @param objects liste alle App zugehörige Kategorie
     */
    public CategorieArrayAdapterSearch(Context context, int resource, ArrayList<AppContact> objects) {
        super(context, 0, objects);

        appcontactList = objects;
        this.context = context;
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
            convertView = LayoutInflater.from(getContext()).inflate(R.layout.list_item_cat_search, parent, false);
        }

        // Lookup view for data population
        TextView tvTitle = (TextView) convertView.findViewById(R.id.appTitle);
        TextView tvAppId = (TextView) convertView.findViewById(R.id.App_id);

        // Populate the data into the template view using the data object
        tvTitle.setText(appContact.title);
        tvAppId.setText(appContact.permissions);

        ivIcon = (ImageView) convertView.findViewById(R.id.myViewIcon);

        DownloadExampleActivity loadBitmap = new DownloadExampleActivity(appContact.icon, ivIcon);
        loadBitmap.downloadPicture();

        // Return the completed view to render on screen
        return convertView;
    }
}
