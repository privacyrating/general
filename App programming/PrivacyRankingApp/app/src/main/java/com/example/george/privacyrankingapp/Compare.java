package com.example.george.privacyrankingapp;

import android.content.Intent;
import android.graphics.Color;
import android.graphics.drawable.GradientDrawable;
import android.os.AsyncTask;
import android.support.design.widget.BottomNavigationView;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.text.SpannableString;
import android.text.SpannableStringBuilder;
import android.text.style.ForegroundColorSpan;
import android.util.Log;
import android.view.MenuItem;
import android.widget.RatingBar;
import android.widget.TextView;
import android.widget.Toast;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

/**
 * Diese Klasse ist fuer die Auflistung von 2 Apps nebeneinander, um sie miteinander zu verlgleichen
 */
public class Compare extends AppCompatActivity {
    private String TAG = Compare.class.getSimpleName();
    private ArrayList<AppCompContact> appCompList;

    private String urlComp = "http://privacyranking.cs.hs-rm.de/app/";

    @Override
    public void onCreate( Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.compare);

        appCompList = new ArrayList<>();

        new Compare.GetContacts().execute();

        /**
         * Layout der Navigationsleiste übergeben.
         * Hier kann man durch klicken auf die Reiter zwischen den Navigationsleisten springen.
         * Außerdem ist hier die Markierung der Navigation festgelegt (setSelectedItemId).
         */
        BottomNavigationView bottomNavigationView = (BottomNavigationView) findViewById(R.id.navigation);
        bottomNavigationView.setSelectedItemId(R.id.navigation_compare);
        bottomNavigationView.setOnNavigationItemSelectedListener(new BottomNavigationView.OnNavigationItemSelectedListener() {

            @Override
            public boolean onNavigationItemSelected(MenuItem item) {
                switch (item.getItemId()) {
                    case R.id.navigation_categorie:
                        Intent intent0 = new Intent(Compare.this, Categorie.class);
                        startActivity(intent0);
                        return true;
                    case R.id.navigation_search:
                        Intent intent1 = new Intent(Compare.this, Search.class);
                        startActivity(intent1);
                        return true;
                    case R.id.navigation_compare:
                        return true;
                    case R.id.navigation_about:
                        Intent intent3 = new Intent(Compare.this, About.class);
                        startActivity(intent3);
                        return true;
                }
                return false;
            }
        });
    }

    private class GetContacts extends AsyncTask<Void, Void, Void> {
        // Erhaelt das uebergebene AppIds aus Categorie12Compare
        Intent intent = getIntent();
        ArrayList<String> appIdList = intent.getStringArrayListExtra("AppIds");

        String appId1 = appIdList.get(0);
        String appId2 = appIdList.get(1);
        JSONObject jsonObject;

        @Override
        protected Void doInBackground(Void... arg0) {
            HttpHandler sh = new HttpHandler();

            // App 1
            String jsonStr1 = sh.makeServiceCall(urlComp + appId1);
            String perm1 = sh.makeServiceCall("http://privacyranking.cs.hs-rm.de/perm/"+appId1);

            // App 2
            String jsonStr2 = sh.makeServiceCall(urlComp + appId2);
            String perm2 = sh.makeServiceCall("http://privacyranking.cs.hs-rm.de/perm/"+appId2);

            HashMap<String, String> nameString1 = new HashMap<>();
            HashMap<String, String> nameString2 = new HashMap<>();


            if (jsonStr1 != null && jsonStr2 != null) {
                ArrayList<String> stringArray = new ArrayList<>();
                ArrayList<HashMap> namePerm = new ArrayList<>();

                stringArray.add(jsonStr1);
                stringArray.add(jsonStr2);

                // Auflistung der einzelnen permissions
                try {
                    JSONArray p1 = new JSONArray(perm1);
                    for (int i = 0; i < p1.length(); i++) {
                        JSONObject pe = p1.getJSONObject(i);

                        if(!pe.getString("name").equals("No Permissions needed.")) {
                            nameString1.put(pe.getString("name"), pe.getString("weight"));
                        }
                    }

                    JSONArray p2 = new JSONArray(perm2);
                    for (int i = 0; i < p2.length(); i++) {
                        JSONObject pe = p2.getJSONObject(i);

                        if(!pe.getString("name").equals("No Permissions needed.")) {
                            nameString2.put(pe.getString("name"), pe.getString("weight"));
                        }
                    }

                    namePerm.add(nameString1);
                    namePerm.add(nameString2);

                } catch (JSONException e) {
                    Log.e(TAG, "Error parsing data jObj " + e.toString());
                }

                int i = 0;
                for(String jsonStr : stringArray){

                    try {
                        jsonObject = new JSONObject(jsonStr);

                        // adding each child node to List
                        AppCompContact tempAppCompContact = new AppCompContact();
                        tempAppCompContact.app_id = "https://play.google.com/store/apps/details?id="+jsonObject.getString("App_id");
                        tempAppCompContact.title = jsonObject.getString("title");
                        tempAppCompContact.rating = jsonObject.getString("rating");
                        tempAppCompContact.min_downloads = jsonObject.getString("min_downloads");
                        tempAppCompContact.similarity = jsonObject.getString("similarity");
                        tempAppCompContact.cost = String.valueOf(Math.round(jsonObject.getInt("cost")/10000)/100.0)+" "+jsonObject.getString("currency");
                        tempAppCompContact.permissons = namePerm.get(i);
                        i++;

                        appCompList.add(tempAppCompContact);

                    } catch (JSONException e) {
                        Log.e(TAG, "Error parsing data jObj " + e.toString());
                    }
                }

            } else {
                Log.e(TAG, "Couldn't get json from server.");
                runOnUiThread(new Runnable() {

                    @Override
                    public void run() {
                        Toast.makeText(getApplicationContext(), "Couldn't get json from server!", Toast.LENGTH_LONG).show();
                    }
                });

            }
            return null;
        }

        /**
         * Ausgabe der einzelnen Informationen, in dem die XML aufgefuellt wird
         */
        @Override
        protected void onPostExecute(Void result) {
            super.onPostExecute(result);

            TextView tvCompTitleApp1 = (TextView) findViewById(R.id.compTitleApp1);
            tvCompTitleApp1.setText(appCompList.get(0).title);

            TextView tvCompTitleApp2 = (TextView) findViewById(R.id.compTitleApp2);
            tvCompTitleApp2.setText(appCompList.get(1).title);


            TextView tvCompPermApp1 = (TextView) findViewById(R.id.compPermApp1);

            // Permission in verschieden Farben darstellen
            HashMap<String, String> permList = appCompList.get(0).permissons;
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
            tvCompPermApp1.setText( builder, TextView.BufferType.SPANNABLE);

            TextView tvCompPermApp2 = (TextView) findViewById(R.id.compPermApp2);

            // Permission in verschieden Farben darstehlen
            HashMap<String, String> permList2 = appCompList.get(1).permissons;
            SpannableStringBuilder builder2 = new SpannableStringBuilder();
            int size2 = permList2.size();

            for (Map.Entry<String, String> entry : permList2.entrySet()) {
                SpannableString str = new SpannableString(entry.getKey());
                float hue = Float.parseFloat(entry.getValue());
                float newHue = 100 - hue * 100;
                float[] hsv = {newHue, 1, 1};

                str.setSpan(new ForegroundColorSpan(Color.HSVToColor(hsv)), 0, str.length(), 0);
                builder2.append(str);

                SpannableString str1;
                if (size2 > 1) {
                    str1 = new SpannableString(", ");
                } else {
                    str1 = new SpannableString(".");
                }
                builder2.append(str1);

                size2--;
            }
            tvCompPermApp2.setText( builder2, TextView.BufferType.SPANNABLE);

            // Sterne Bewertung vom PlayStore
            RatingBar tvRating1 = (RatingBar) findViewById(R.id.compRatApp1);
            int rating = Integer.valueOf(appCompList.get(0).rating);
            tvRating1.setRating(rating);

            RatingBar tvRating2 = (RatingBar) findViewById(R.id.compRatApp2);
            int rating2 = Integer.valueOf(appCompList.get(1).rating);
            tvRating2.setRating(rating2);

            GradientDrawable gradient;
            float hue, newHue;
            TextView tvCompPrivRatApp1 = (TextView) findViewById(R.id.compPrivRatApp1);
            hue = Float.parseFloat(appCompList.get(0).similarity);
            newHue = (hue * 120) / 100;
            float[] hsv1 = {newHue, 1, 1};

            gradient = new GradientDrawable(GradientDrawable.Orientation.LEFT_RIGHT, new int[]{Color.GREEN, Color.HSVToColor(hsv1)});
            gradient.setShape(GradientDrawable.RECTANGLE);
            tvCompPrivRatApp1.setBackgroundDrawable(gradient);


            TextView tvCompPrivRatApp2 = (TextView) findViewById(R.id.compPrivRatApp2);
            hue = Float.parseFloat(appCompList.get(1).similarity);
            newHue = (hue * 120) / 100;
            float[] hsv2 = {newHue, 1, 1};

            gradient = new GradientDrawable(GradientDrawable.Orientation.LEFT_RIGHT, new int[]{Color.GREEN, Color.HSVToColor(hsv2)});
            gradient.setShape(GradientDrawable.RECTANGLE);
            tvCompPrivRatApp2.setBackgroundDrawable(gradient);

            TextView tvCompMinDowApp1 = (TextView) findViewById(R.id.compMinDowApp1);
            tvCompMinDowApp1.setText(appCompList.get(0).min_downloads);

            TextView tvCompMinDowApp2 = (TextView) findViewById(R.id.compMinDowApp2);
            tvCompMinDowApp2.setText(appCompList.get(1).min_downloads);

            TextView tvCompCostApp1 = (TextView) findViewById(R.id.compCostApp1);
            tvCompCostApp1.setText(appCompList.get(0).cost);

            TextView tvCompCostApp2 = (TextView) findViewById(R.id.compCostApp2);
            tvCompCostApp2.setText(appCompList.get(1).cost);

            TextView tvCompLinkApp1 = (TextView) findViewById(R.id.compLinkApp1);
            tvCompLinkApp1.setText(appCompList.get(0).app_id);

            TextView tvCompLinkApp2 = (TextView) findViewById(R.id.compLinkApp2);
            tvCompLinkApp2.setText(appCompList.get(1).app_id);

        }
    }
}