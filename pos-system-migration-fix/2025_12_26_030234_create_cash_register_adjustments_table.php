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
        if (!Schema::hasTable('cash_register_adjustments')) {
            Schema::create('cash_register_adjustments', function (Blueprint $table) {
                $table->id();
                $table->foreignId('cash_register_session_id')->constrained()->onDelete('cascade');
                $table->foreignId('user_id')->constrained()->onDelete('cascade'); // Requester (Manager)
                $table->foreignId('approved_by')->nullable()->constrained('users')->onDelete('set null'); // Approver (Admin)
                $table->decimal('original_amount', 10, 2);
                $table->decimal('new_amount', 10, 2);
                $table->text('reason'); // Required
                $table->enum('status', ['pending', 'approved', 'rejected'])->default('pending');
                $table->timestamps();
            });
        }
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('cash_register_adjustments');
    }
};
