package com.example.george.privacyrankingapp;

import android.app.ProgressDialog;
import android.content.Intent;
import android.os.AsyncTask;
import android.support.annotation.NonNull;
import android.support.design.widget.BottomNavigationView;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.MenuItem;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ListAdapter;
import android.widget.ListView;
import android.widget.SimpleAdapter;
import android.widget.Toast;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;

import static com.example.george.privacyrankingapp.R.id.title;

/**
 * Diese Klasse ist fuer die Auflistung der Kategorien zustaendig
 */
public class Categorie extends AppCompatActivity {

    private String TAG = Categorie.class.getSimpleName();
    private ProgressDialog pDialog;
    private ListView lv;
    private static String url = "http://privacyranking.cs.hs-rm.de/cat";
    private static final int MAX_CHECKED_CHECKBOXES = 2;
    private HashSet<String> chosenAppIds;
    private static final int LENGTH_TIME = 3500;

    private static final int LONG_DELAY = 3500; // 3.5 seconds
    private static final int SHORT_DELAY = 2000; // 2 seconds

    ArrayList<HashMap<String, String>> contactList;

    /**
     * Die Methode onCreate() muss in jedem Android Activity implementiert sein.
     * Sie erzeugt das Activity
     */
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);


        // lädt die Benutzerschnittstelle aus der Datei res/layout/activity_main.xml.
        setContentView(R.layout.activity_main);
        contactList = new ArrayList<>();
        lv = (ListView) findViewById(R.id.list);
        chosenAppIds = new HashSet<String>();
        new Categorie.GetContacts().execute();

        /**
         * Layout der Navigationsleiste übergeben.
         * Hier kann man durch klicken auf die Reiter zwischen den Navigationsleisten springen.
         * Außerdem ist hier die Markierung der Navigation festgelegt (setSelectedItemId).
         * Reiter Compare ist nicht anklickbar
         */
        final BottomNavigationView bottomNavigationView = (BottomNavigationView) findViewById(R.id.navigation);
        bottomNavigationView.setSelectedItemId(R.id.navigation_categorie);
        bottomNavigationView.setOnNavigationItemSelectedListener(new BottomNavigationView.OnNavigationItemSelectedListener() {

            @Override
            public boolean onNavigationItemSelected(@NonNull MenuItem item) {
                switch (item.getItemId()) {
                    case R.id.navigation_categorie:
                        Intent intent0 = new Intent(Categorie.this, Categorie.class);
                        startActivity(intent0);
                        return true;
                    case R.id.navigation_search:
                        Intent intent1 = new Intent(Categorie.this, Search.class);
                        startActivity(intent1);
                        return true;
                    case R.id.navigation_about:
                        Intent intent3 = new Intent(Categorie.this, About.class);
                        startActivity(intent3);
                        return true;
                }
                return false;
            }
        });
    }

    private class GetContacts extends AsyncTask<Void, Void, Void> {
        @Override
        protected void onPreExecute() {
            super.onPreExecute();
            // Zeigt den Progressdialog an
            pDialog = new ProgressDialog(Categorie.this);
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
            String jsonStr = sh.makeServiceCall(url);

            Log.e(TAG, "Response from url: " + jsonStr);

            if (jsonStr != null) {
                try {
                    // Erstelle eine Array Liste mit dem Inhalt
                    JSONArray jarray = new JSONArray(jsonStr);

                    /*
                     * Durchlauf des JSONArray und Auflistung der einzelnen Cluster mit Namen(Kategorie).
                     * Wir nehmen "name" und "Cluster_id" und speichern es in Strings.
                     * Erstellen einer HashMap und füllen "name" und "Cluster_id" der Liste hinzu.
                     */
                    for (int i = 0; i < jarray.length(); i++) {
                        JSONObject c = jarray.getJSONObject(i);

                        String title = c.getString("name");
                        String Cluster_id = c.getString("Cluster_id");

                        HashMap<String, String> contact = new HashMap<>();

                        contact.put("name", title);
                        contact.put("Cluster_id", Cluster_id);

                        contactList.add(contact);
                    }

                    // Fehlerausgabe beim parsen
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

            // Erstelle einen ListAdapter, mit welchem für jedes Element des Arrays die Ausgabe stattfindet
            final ListAdapter adapter = new SimpleAdapter(
                    Categorie.this, contactList,
                    R.layout.list_itemm, new String[]{"name"}, new int[]{title});

            // Wird der Listview als adapter festgelegt.
            lv.setAdapter(adapter);

            /**
             * Beim anklicken einer Kategorie, wird von der Position die Cluster_id gespeichert
             * und an Categorie12 übergeben.
             * Durch startActivity gelangt man dann zur nächsten Seite.
              */
            lv.setOnItemClickListener(new android.widget.AdapterView.OnItemClickListener() {
                @Override
                public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
                    Intent intent = new Intent(Categorie.this, Categorie12.class);
                    HashMap<String, Object> obj = (HashMap<String, Object>) adapter.getItem(position);
                    String name = (String) obj.get("Cluster_id");
                    intent.putExtra("Cluster_ID", name);
                    startActivity(intent);
                    for (int i = 0; i < 2; i++) {
                        Toast.makeText(getApplicationContext(),
                                "Compare function is now available, please click on the 3rd tab", Toast.LENGTH_LONG).show();
                    }
                }
            });
        }
    }
}

