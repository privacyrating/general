package com.example.george.privacyrankingapp;

import android.app.ProgressDialog;
import android.content.Intent;
import android.os.AsyncTask;
import android.os.Bundle;
import android.support.design.widget.BottomNavigationView;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.MenuItem;
import android.view.View;
import android.widget.AdapterView;
import android.widget.CheckBox;
import android.widget.ListView;
import android.widget.Toast;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.HashSet;

/**
 * Diese Klasse ist fuer die Compare zustaendig
 */
public class Categorie12Compare extends AppCompatActivity {

    private String TAG = Categorie12.class.getSimpleName();
    private static final int MAX_CHECKED_CHECKBOXES = 2;
    private ProgressDialog pDialog;
    private ListView lv;
    private int checkboxCounter;
    private ArrayList<AppContact> appContactList;
    private HashSet<String> chosenAppIds;

    /**
     * Die Methode onCreate() muss in jedem Android Activity implementiert sein.
     * Sie erzeugt das Activity
     */
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // laedt die Benutzerschnittstelle aus der Datei res/layout/activity_main.xml.
        setContentView(R.layout.activity_main);

        // keine Checkbox Felder markiert
        checkboxCounter = 0;
        appContactList = new ArrayList<>();
        chosenAppIds = new HashSet<String>();
        lv = (ListView) findViewById(R.id.list);

        // Pop-Up Meldung erscheint für das Markieren von 2 Apps
        Toast.makeText(Categorie12Compare.this, "Choose 2 apps", Toast.LENGTH_SHORT).show();
        new Categorie12Compare.GetContacts().execute();

        /**
         * Layout der Navigationsleiste uebergeben.
         * Hier kann man durch klicken auf die Reiter zwischen den Navigationsleisten springen.
         * Außerdem ist hier die Markierung der Navigation festgelegt (setSelectedItemId).
         */
        final BottomNavigationView bottomNavigationView = (BottomNavigationView) findViewById(R.id.navigation);
        bottomNavigationView.setSelectedItemId(R.id.navigation_compare);
        bottomNavigationView.setOnNavigationItemSelectedListener(new BottomNavigationView.OnNavigationItemSelectedListener() {

            @Override
            public boolean onNavigationItemSelected(MenuItem item) {
                switch (item.getItemId()) {
                    case R.id.navigation_categorie:
                        Intent intent0 = new Intent(Categorie12Compare.this, Categorie.class);
                        startActivity(intent0);
                        return true;
                    case R.id.navigation_search:
                        Intent intent1 = new Intent(Categorie12Compare.this, Search.class);
                        startActivity(intent1);
                        return true;
                    case R.id.navigation_compare:
                        if(chosenAppIds.size() != MAX_CHECKED_CHECKBOXES){
                            // todo text
                            Toast.makeText(Categorie12Compare.this, "Choose 2 apps", Toast.LENGTH_SHORT).show();
                        }
                        return true;
                    case R.id.navigation_about:
                        Intent intent3 = new Intent(Categorie12Compare.this, About.class);
                        startActivity(intent3);
                        return true;
                }
                return false;
            }
        });
    }


    /**
     * Beim markieren von 2 Apps durch das Kontrollkaestchen, springt er auf die naechste Seite (Compare),
     * wo dann die Apps nebeneinander aufgelistet bzw. verglichen werden.
     */
    public void onCheckboxClicked(View view) {
        // Check which checkbox was clicked
        switch(view.getId()) {
            case R.id.Comp_id:
                CheckBox checkbox = (CheckBox) view.findViewById(R.id.Comp_id);
                AppContact appContact = (AppContact) checkbox.getTag();
                if (checkbox.isChecked()){
                    if(checkboxCounter+1 > MAX_CHECKED_CHECKBOXES){
                        checkbox.setChecked(false);
                        appContact.checkboxChecked = false;
                        // todo change text
                        Toast.makeText(this, "Failure: Max 2", Toast.LENGTH_SHORT).show();
                    } else {
                        appContact.checkboxChecked = true;
                        checkboxCounter++;
                        chosenAppIds.add(appContact.appId);
                        if(checkboxCounter == 2){
                            Intent intent2 = new Intent(Categorie12Compare.this, Compare.class);
                            ArrayList<String> appIdsList = new ArrayList<String>();
                            for(String appC : chosenAppIds){
                                appIdsList.add(appC);
                            }
                            intent2.putExtra("AppIds", appIdsList);
                            startActivity(intent2);                        }
                    }
                } else {
                    checkboxCounter--;
                    appContact.checkboxChecked = false;
                    chosenAppIds.remove(appContact.appId);
                }
                break;
        }
    }



    private class GetContacts extends AsyncTask<Void, Void, Void> {

        // Erhaelt das uebergebene Cluster_id aus Categorie
        Bundle intent = getIntent().getExtras();
        String pos = intent.getString("Cluster_ID");

        @Override
        protected void onPreExecute() {
            super.onPreExecute();
            // Zeigt den Progressdialog an
            pDialog = new ProgressDialog(Categorie12Compare.this);
            pDialog.setMessage("Please wait...");
            pDialog.setCancelable(false);
            pDialog.show();

        }

        /**
         * doInBackground verarbeitet die Threads im Hintergrund
         */
        @Override
        protected Void doInBackground(Void... arg0) {
            HttpHandler sh = new HttpHandler();

            // Anfrage an den Server schicken und erhalten eine Antwort
            String jsonStr = sh.makeServiceCall("http://privacyranking.cs.hs-rm.de/cat/"+pos);

            if (jsonStr != null) {
                try {
                    // Erstelle eine Array Liste mit dem Inhalt
                    JSONArray jarray = new JSONArray(jsonStr);

                    /**
                     * Durchlauf des JSONArray und Auflistung der einzelnen Cluster mit Namen(Kategorie).
                     * Wir nehmen die Daten und speichern sie in Strings.
                     * Erstellen einer HashMap und fuellen diese mit den Daten und fuegen Sie unserer Liste hinzu.
                     */
                    for (int i = 0; i < jarray.length(); i++) {
                        JSONObject c = jarray.getJSONObject(i);

                        String title = c.getString("title");
                        String App_id = c.getString("App_id");
                        String similarity = c.getString("similarity");
                        String icon = c.getString("icon");
                        String permissions = c.getString("count(Permission_id)");

                        AppContact tempAppContact = new AppContact();
                        tempAppContact.title = title;
                        tempAppContact.appId = App_id;
                        tempAppContact.similarity = similarity;
                        tempAppContact.icon = icon;
                        tempAppContact.permissions = permissions+" permission(s)";

                        appContactList.add(tempAppContact);
                    }

                    // Fehlerausgabe beim parsen
                } catch (final JSONException e) {
                    Log.e(TAG, "Json parsing error: " + e.getMessage());
                    runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            Toast.makeText(getApplicationContext(), "Json parsing error: " + e.getMessage(), Toast.LENGTH_LONG).show();
                        }
                    });

                }

                // Fehlerausgabe, falls Server oder Datei nicht erreichbar
            } else {
                Log.e(TAG, "Couldn't get json from server.");
                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        Toast.makeText(getApplicationContext(),
                                "Couldn't get json from server. Check LogCat for possible errors!",
                                Toast.LENGTH_LONG)
                                .show();
                    }
                });
            }
            return null;
        }

        /**
         * Liefert die Ergebnisse von doInBackground()
         */
        @Override
        protected void onPostExecute(Void result) {
            super.onPostExecute(result);
            // verlaesst den Progressdialog
            if (pDialog.isShowing())
                pDialog.dismiss();

            // Greifen auf den Adapter zu
            final CategorieArrayAdapterCompare catAdapter = new CategorieArrayAdapterCompare(Categorie12Compare.this, 0, appContactList);

            // Wird der Listview als adapter festgelegt.
            lv.setAdapter(catAdapter);

            /**
             * Beim anklicken einer Kategorie, wird von der Position die AppID gespeichert
             * und an Categorie3 übergeben.
             * Durch startActivity gelangt man dann zur nächsten Seite.
             */
            lv.setOnItemClickListener(new android.widget.AdapterView.OnItemClickListener() {

                @Override
                public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
                    Intent intent = new Intent(Categorie12Compare.this, Categorie3.class);
                    AppContact name = (AppContact) catAdapter.getItem(position);
                    intent.putExtra("AppID", name.appId);
                    startActivity(intent);
                }
            });
        }
    }
}