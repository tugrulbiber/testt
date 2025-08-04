package com.example.commitscanner.service;

import org.springframework.http.*;
import org.springframework.web.client.RestTemplate;
import java.util.Map;

public class AiServiceClient {

    private final RestTemplate restTemplate = new RestTemplate();
    private final String aiapiUrl = "http://localhost:8000/analyze";

    public Map<String, Object> analyzeCommit(Map<String, Object> commitData) {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        HttpEntity<Map<String, Object>> request = new HttpEntity<>(commitData, headers);
        ResponseEntity<Map> response = restTemplate.postForEntity(aiapiUrl, request, Map.class);

        if(response.getStatusCode() == HttpStatus.OK) {
            return response.getBody();
        } else {
            throw new RuntimeException("AI analysis failed with status: " + response.getStatusCode());
        }
    }
}
