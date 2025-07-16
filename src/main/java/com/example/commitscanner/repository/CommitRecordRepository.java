package com.example.commitscanner.repository;

import com.example.commitscanner.entity.CommitRecord;
import org.springframework.data.jpa.repository.JpaRepository;

public interface CommitRecordRepository extends JpaRepository<CommitRecord, String> {

    // ✅ Commit hash varsa true döner
    boolean existsByCommitHash(String commitHash);
}
