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
 * Diese Klasse liefert die Ergebnisse der Suchfunktion
 */
public class Search2 extends AppCompatActivity {
    private String TAG = Search2.class.getSimpleName();

    private static final int MAX_CHECKED_CHECKBOXES = 2;

    private ProgressDialog pDialog;
    private ListView lv;

    private int checkboxCounter;
    private ArrayList<AppContact> appContactList;
    private HashSet<String> chosenAppIds;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        checkboxCounter = 0;
        appContactList = new ArrayList<>();
        chosenAppIds = new HashSet<String>();

        lv = (ListView) findViewById(R.id.list);

        new Search2.GetContacts().execute();

        final BottomNavigationView bottomNavigationView = (BottomNavigationView) findViewById(R.id.navigation);
        bottomNavigationView.setSelectedItemId(R.id.navigation_search);
        bottomNavigationView.setOnNavigationItemSelectedListener(new BottomNavigationView.OnNavigationItemSelectedListener() {

            @Override
            public boolean onNavigationItemSelected(MenuItem item) {
                switch (item.getItemId()) {
                    case R.id.navigation_categorie:
                        Intent intent0 = new Intent(Search2.this, Categorie.class);
                        startActivity(intent0);
                        return true;
                    case R.id.navigation_search:
                        Intent intent1 = new Intent(Search2.this, Search.class);
                        startActivity(intent1);
                        return true;
                    case R.id.navigation_about:
                        Intent intent3 = new Intent(Search2.this, About.class);
                        startActivity(intent3);
                        return true;
                }
                return false;
            }
        });
    }

    private class GetContacts extends AsyncTask<Void, Void, Void> {
        Bundle intent = getIntent().getExtras();
        String pos = intent.getString("query");
        @Override
        protected void onPreExecute() {
            super.onPreExecute();
            // Showing progress dialog
            pDialog = new ProgressDialog(Search2.this);
            pDialog.setMessage("Please wait...");
            pDialog.setCancelable(false);
            pDialog.show();
        }

        @Override
        protected Void doInBackground(Void... arg0) {
            HttpHandler sh = new HttpHandler();

            // Making a request to url and getting response
            String jsonStr = sh.makeServiceCall("http://privacyranking.cs.hs-rm.de/search/"+pos);

            Log.e(TAG, "Response from url: " + jsonStr);

            if (jsonStr != null) {
                try {
                    JSONArray jarray = new JSONArray(jsonStr);

                    for (int i = 0; i < jarray.length(); i++) {
                        JSONObject c = jarray.getJSONObject(i);

                        String title = c.getString("title");
                        String App_id = c.getString("App_id");
                        String icon = c.getString("icon");
                        String permissions = c.getString("count(Permission_id)");

                        // adding each child node to List
                        AppContact tempAppContact = new AppContact();
                        tempAppContact.title = title;
                        tempAppContact.appId = App_id;
                        tempAppContact.icon = icon;
                        tempAppContact.permissions = permissions+" permission(s)";

                        appContactList.add(tempAppContact);
                    }

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


        @Override
        protected void onPostExecute(Void result) {
            super.onPostExecute(result);
            if (pDialog.isShowing())
                pDialog.dismiss();

            final CategorieArrayAdapterSearch catAdapter = new CategorieArrayAdapterSearch(Search2.this, 0, appContactList);

            lv.setAdapter(catAdapter);
            lv.setOnItemClickListener(new android.widget.AdapterView.OnItemClickListener() {

                @Override
                public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
                    Intent intent = new Intent(Search2.this, Categorie3.class);
                    AppContact name = (AppContact) catAdapter.getItem(position);
                    intent.putExtra("AppID", name.appId);
                    startActivity(intent);
                }
            });
        }
    }
}