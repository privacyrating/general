package com.example.george.privacyrankingapp;


import android.app.ProgressDialog;
import android.content.Intent;
import android.os.AsyncTask;
import android.os.Bundle;
import android.support.annotation.NonNull;
import android.support.design.widget.BottomNavigationView;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.MenuItem;
import android.widget.ListView;
import android.widget.Toast;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.HashMap;

/**
 * Diese Klasse ist fuer die App Beschreibung zustaendig, Sie liefert die Ergebnisse
 */
public class Categorie3 extends AppCompatActivity {

    private String TAG = Categorie3.class.getSimpleName();

    private ProgressDialog pDialog;
    private ListView lv;
    private ArrayList<AppContact> appContactList;

    /**
     * Die Methode onCreate() muss in jedem Android Activity implementiert sein.
     * Sie erzeugt das Activity
     */
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        // laedt die Benutzerschnittstelle aus der Datei res/layout/activity_main.xml.
        setContentView(R.layout.activity_main);

        appContactList = new ArrayList<>();

        lv = (ListView) findViewById(R.id.list);
        new Categorie3.GetContacts().execute();

        /**
         * Layout der Navigationsleiste übergeben.
         * Hier kann man durch klicken auf die Reiter zwischen den Navigationsleisten springen.
         * Außerdem ist hier die Markierung der Navigation festgelegt (setSelectedItemId).
         * Reiter Compare ist nicht anklickbar
         */
        final BottomNavigationView bottomNavigationView = (BottomNavigationView) findViewById(R.id.navigation);
        bottomNavigationView.setOnNavigationItemSelectedListener(new BottomNavigationView.OnNavigationItemSelectedListener() {

            @Override
            public boolean onNavigationItemSelected(@NonNull MenuItem item) {
                switch (item.getItemId()) {
                    case R.id.navigation_categorie:
                        Intent intent0 = new Intent(Categorie3.this, Categorie.class);
                        startActivity(intent0);
                        return true;
                    case R.id.navigation_search:
                        Intent intent1 = new Intent(Categorie3.this, Search.class);
                        startActivity(intent1);

                        return true;
                    case R.id.navigation_about:
                        Intent intent3 = new Intent(Categorie3.this, About.class);
                        startActivity(intent3);
                        return true;
                }
                return false;
            }
        });
    }

    private class GetContacts extends AsyncTask<Void, Void, Void> {
        // Erhält das übergebene AppID aus Categorie12
        Bundle intent = getIntent().getExtras();
        String AppID = intent.getString("AppID");

        @Override
        protected void onPreExecute() {
            super.onPreExecute();
            // Showing progress dialog
            pDialog = new ProgressDialog(Categorie3.this);
            pDialog.setMessage("Please wait...");
            pDialog.setCancelable(false);
            pDialog.show();
            System.out.println(AppID);
        }

        /**
         * doInBackground verarbeitet die Threads im Hintergrund
         */
        @Override
        protected Void doInBackground(Void... arg0) {
            HttpHandler sh = new HttpHandler();

            // Making a request to url and getting response
            String jsonStr = sh.makeServiceCall("http://privacyranking.cs.hs-rm.de/app/"+AppID);
            String perm = sh.makeServiceCall("http://privacyranking.cs.hs-rm.de/perm/"+AppID);

            HashMap<String, String> permList = new HashMap<>();

            if (jsonStr != null) {
                try {
                    /**
                     * Erstelle ein JSONObject mit dem Inhalt
                     * Erstelle eine Array Liste mit dem Inhalt der Permissions
                     * Durchlauf des JSONArray und Auflistung der einzelnen permissions.
                     * Wir nehmen die Daten und speichern sie in Strings.
                     */
                    JSONObject c = new JSONObject(jsonStr);

                    JSONArray p = new JSONArray(perm);
                    for (int i = 0; i < p.length(); i++) {
                        JSONObject pe = p.getJSONObject(i);

                        if(!pe.getString("name").equals("No Permissions needed.")) {
                            permList.put(pe.getString("name"), pe.getString("weight"));
                        }
                    }

                    // Fügt App Informationen der appContactList hinzu
                    String title = c.getString("title");
                    String title_en = c.getString("title_en");
                    String description = c.getString("description");
                    String rating = c.getString("rating");
                    String min_downloads = c.getString("min_downloads");
                    double cost = Math.round(c.getInt("cost")/10000)/100.0;
                    String currency = c.getString("currency");
                    String changelog = c.getString("changelog");
                    String App_id = c.getString("App_id");
                    String similarity = c.getString("similarity");

                    AppContact tempAppContact = new AppContact();
                    tempAppContact.title = title;
                    tempAppContact.title_en = title_en;
                    tempAppContact.permissionsList = permList;
                    tempAppContact.description = description;
                    tempAppContact.rating = rating;
                    tempAppContact.min_downloads = min_downloads;
                    tempAppContact.cost = cost + " " + currency;
                    tempAppContact.changelog = changelog;
                    tempAppContact.link = "https://play.google.com/store/apps/details?id=" + App_id;
                    tempAppContact.appId = App_id;
                    tempAppContact.similarity = similarity;

                    appContactList.add(tempAppContact);
                } catch (final JSONException e) {
                    Log.e(TAG, "Json parsing error: " + e.getMessage());
                    runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            Toast.makeText(getApplicationContext(),
                                    "Json parsing error: " + e.getMessage(),
                                    Toast.LENGTH_LONG)
                                    .show();
                        }
                    });
                }
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
            if (pDialog.isShowing())
                pDialog.dismiss();

            final CategorieArrayAdapterInfo catAdapter = new CategorieArrayAdapterInfo(Categorie3.this, 0, appContactList);

            lv.setAdapter(catAdapter);
        }
    }
}