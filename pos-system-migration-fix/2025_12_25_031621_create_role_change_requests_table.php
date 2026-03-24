<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        if (!Schema::hasTable('role_change_requests')) {
            Schema::create('role_change_requests', function (Blueprint $table) {
                $table->id();
                $table->foreignId('requester_id')->constrained('users')->onDelete('cascade');
                $table->foreignId('approver_id')->constrained('users')->onDelete('cascade');
                $table->foreignId('target_user_id')->constrained('users')->onDelete('cascade');
                $table->string('new_role');
                $table->enum('status', ['pending', 'approved', 'rejected', 'consumed'])->default('pending');
                $table->timestamp('expires_at');
                $table->timestamps();
            });
        }
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('role_change_requests');
    }
};
