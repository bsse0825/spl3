package com.tushar.neuralkeyboard;

import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.View;
import android.view.inputmethod.InputMethodInfo;
import android.view.inputmethod.InputMethodManager;
import android.widget.LinearLayout;
import android.widget.Toast;

import com.google.android.gms.ads.AdRequest;
import com.google.android.gms.ads.AdView;
import com.tushar.neuralkeyboard.android.ImePreferences;

import java.util.List;


public class MainActivity extends AppCompatActivity
        implements View.OnClickListener {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        LinearLayout enableSetting = findViewById(R.id.layout_EnableSetting);
        LinearLayout addKeyboards = findViewById(R.id.layout_AddLanguages);
        LinearLayout chooseInputMethod = findViewById(R.id.layout_ChooseInput);
        LinearLayout chooseTheme = findViewById(R.id.layout_ChooseTheme);
        //LinearLayout manageDictionaries = findViewById(R.id.layout_ManageDictionary);
        LinearLayout about = findViewById(R.id.layout_about);

        enableSetting.setOnClickListener(this);
        addKeyboards.setOnClickListener(this);
        chooseInputMethod.setOnClickListener(this);
        chooseTheme.setOnClickListener(this);
       // manageDictionaries.setOnClickListener(this);
        about.setOnClickListener(this);

        AdView adView = this.findViewById(R.id.adView);
        AdRequest adRequest = new AdRequest.Builder()
                .addTestDevice(AdRequest.DEVICE_ID_EMULATOR)
                .addTestDevice("D17FE6D8441E3F2375E3709A2EED851B")
                .build();
        adView.loadAd(adRequest);
    }


    @Override
    public void onClick(View view) {
        switch (view.getId()) {
            case R.id.layout_EnableSetting:
                startActivityForResult(
                        new Intent(android.provider.Settings.ACTION_INPUT_METHOD_SETTINGS), 0);
                break;
            case R.id.layout_AddLanguages:
                lunchPreferenceActivity();
                break;
            case R.id.layout_ChooseInput:
                if (isInputEnabled()) {
                    ((InputMethodManager) getApplicationContext().getSystemService(Context.INPUT_METHOD_SERVICE))
                            .showInputMethodPicker();
                } else {
                    Toast.makeText(this, "Please enable keyboard first.", Toast.LENGTH_SHORT).show();
                }
                break;
            case R.id.layout_ChooseTheme:
                startActivity(new Intent(this, ThemeActivity.class));
                break;
            case R.id.layout_ManageDictionary:
                startActivity(new Intent(this, DictionaryActivity.class));
                break;
            case R.id.layout_about:
                startActivity(new Intent(this, AboutActivity.class));
                break;
            default:
                break;
        }
    }


    public boolean isInputEnabled() {
        InputMethodManager imm = (InputMethodManager) getSystemService(Context.INPUT_METHOD_SERVICE);
        List<InputMethodInfo> mInputMethodProperties = imm.getEnabledInputMethodList();

        final int N = mInputMethodProperties.size();
        boolean isInputEnabled = false;

        for (int i = 0; i < N; i++) {

            InputMethodInfo imi = mInputMethodProperties.get(i);
            Log.d("INPUT ID", String.valueOf(imi.getId()));
            if (imi.getId().contains(getPackageName())) {
                isInputEnabled = true;
            }
        }

        if (isInputEnabled) {
            return true;
        } else {
            return false;
        }
    }

    public void lunchPreferenceActivity() {
        if (isInputEnabled()) {
            Intent intent = new Intent(this, ImePreferences.class);
            startActivity(intent);
        } else {
            Toast.makeText(this, "Please enable keyboard first.", Toast.LENGTH_SHORT).show();
        }
    }
}