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
import android.widget.ListView;
import android.widget.Toast;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.HashSet;

/**
 * Diese Klasse ist fuer die Auflistung der Apps einer Kategorie zustaendig
 */
public class Categorie12 extends AppCompatActivity {

    private String TAG = Categorie12.class.getSimpleName();
    private static final int MAX_CHECKED_CHECKBOXES = 2;
    private ProgressDialog pDialog;
    private ListView lv;
    private ArrayList<AppContact> appContactList;
    private int checkboxCounter;
    private HashSet<String> chosenAppIds;

    /**
     * Die Methode onCreate() muss in jedem Android Activity implementiert sein.
     * Sie erzeugt das Activity
     */

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // lädt die Benutzerschnittstelle aus der Datei res/layout/activity_main.xml.
        setContentView(R.layout.activity_main);

        // keine Checkbox Felder markiert und nicht sichtbar
        checkboxCounter = 0;
        chosenAppIds = new HashSet<String>();
        appContactList = new ArrayList<>();
        lv = (ListView) findViewById(R.id.list);
        new Categorie12.GetContacts().execute();

        /**
         * Layout der Navigationsleiste übergeben.
         * Hier kann man durch klicken auf die Reiter zwischen den Navigationsleisten springen.
         * Außerdem ist hier die Markierung der Navigation festgelegt (setSelectedItemId).
         */
        final BottomNavigationView bottomNavigationView = (BottomNavigationView) findViewById(R.id.navigation);
        bottomNavigationView.setSelectedItemId(R.id.navigation_categorie);
        bottomNavigationView.setOnNavigationItemSelectedListener(new BottomNavigationView.OnNavigationItemSelectedListener() {

            @Override
            public boolean onNavigationItemSelected(MenuItem item) {
                Bundle intent = getIntent().getExtras();
                String pos = intent.getString("Cluster_ID");
                switch (item.getItemId()) {
                    case R.id.navigation_categorie:
                        Intent intent0 = new Intent(Categorie12.this, Categorie.class);
                        startActivity(intent0);
                        return true;
                    case R.id.navigation_search:
                        Intent intent1 = new Intent(Categorie12.this, Search.class);
                        startActivity(intent1);
                        return true;
                    case R.id.navigation_compare:
                        Intent intent2 = new Intent(Categorie12.this, Categorie12Compare.class);
                        intent2.putExtra("Cluster_ID", pos);
                        startActivity(intent2);
                        return true;
                    case R.id.navigation_about:
                        Intent intent3 = new Intent(Categorie12.this, About.class);
                        startActivity(intent3);
                        return true;
                }
                return false;
            }
        });

    }

    private class GetContacts extends AsyncTask<Void, Void, Void> {

        // Erhaelt das uebergebene Cluster_id aus Categorie
        Bundle intent = getIntent().getExtras();
        String pos = intent.getString("Cluster_ID");

        @Override
        protected void onPreExecute() {
            super.onPreExecute();
            // Zeigt den Progressdialog an
            pDialog = new ProgressDialog(Categorie12.this);
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
            // verlässt den Progressdialog
            if (pDialog.isShowing())
                pDialog.dismiss();

            // Greifen auf den Adapter zu
            final CategorieArrayAdapter catAdapter = new CategorieArrayAdapter(Categorie12.this, 0, appContactList);

            // Wird der Listview als adapter festgelegt.
            lv.setAdapter(catAdapter);

            /**
             * Beim anklicken einer Kategorie, wird von der Position die AppID gespeichert
             * und an Categorie3 übergeben.
             * Durch startActivity gelangt man dann zur naechsten Seite.
             */
            lv.setOnItemClickListener(new android.widget.AdapterView.OnItemClickListener() {

                @Override
                public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
                    Intent intent = new Intent(Categorie12.this, Categorie3.class);
                    AppContact name = (AppContact) catAdapter.getItem(position);
                    intent.putExtra("AppID", name.appId);
                    startActivity(intent);
                }
            });
        }
    }
}